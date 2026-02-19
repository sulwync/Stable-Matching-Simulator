from __future__ import annotations

from collections import deque
import time
from typing import Any, Optional

from core.types import (
    ResidentId, HospitalId, ResidentPreferences, HospitalPreferences, CapacityMap,
    RankTable, ResidentMatch, HospitalMatch, HospitalHeld, EventLog, FreeQueue,
    ResidentsInfoMap, HospitalsCriteriaMap, StableMatchReturn)

def buildRank(hosPref: HospitalPreferences) -> RankTable:
    return {h: {r: i for i, r in enumerate(prefs)} for h, prefs in hosPref.items()}

def worstHeld(h: HospitalId, held: list[ResidentId], rank: RankTable) -> ResidentId:
    worst = held[0]
    worstRank = rank[h][worst]
    for r in held[1:]:
        rRank = rank[h][r]
        if rRank > worstRank:
            worst, worstRank = r, rRank
    return worst

def stableMatch( 
        resPref: ResidentPreferences,
        hosPref: HospitalPreferences, 
        capacity: CapacityMap, 
        returnEvents: bool=False) -> StableMatchReturn:

    start = time.perf_counter()
    rank = buildRank(hosPref)
    events: EventLog = []

    def log(line: str) -> None:
        if returnEvents:
            events.append(line)

    # Initialize state
    resident: list[ResidentId] = list(resPref.keys())
    hospital: list[HospitalId] = list(hosPref.keys())
    
    nextChoice: dict[ResidentId, int] = {r: 0 for r in resident}
    resMatch: ResidentMatch = {r: None for r in resident}
    hosHeld: HospitalHeld = {h: [] for h in hospital}

    free: FreeQueue = deque([r for r in resident if len(resPref.get(r, [])) > 0])
    log(f"START: {list(free)}")

    while free:
        r = free.popleft()
        log(f"Resident Selected: {r}, Queue: {list(free)}")

        if resMatch[r] is not None:
            continue

        prefs = resPref.get(r, [])
        if nextChoice[r] >= len(prefs):
            log(f"Exhausted: {r}")
            continue # no more hospitals to propose to

        h = prefs[nextChoice[r]]
        log(f"Proposal: {r} -> {h}, Preference Index: {nextChoice[r]}")

        nextChoice[r] += 1

        # Reject if invalid hospital or no capacity
        if h not in capacity or capacity[h] <= 0 or h not in hosHeld:
            log(f"Reject: {r}, No Capacity or Invalid: {h}")
            if nextChoice[r] < len(prefs):
                free.append(r)
                log(f"Requeue: {r}, Next Choice Index: {nextChoice[r]}")
            else:
                log(f"Exhausted After Reject: {r}")
            continue

        if r not in rank.get(h, {}):
            log(f"Reject Unranked: {r} -> {h}")
            if nextChoice[r] < len(prefs):
                free.append(r)
                log(f"Requeue Unranked: {r}, Next Choice Index: {nextChoice[r]}")
            else:
                log(f"Exhausted After Unranked Reject: {r}")
            continue

        hosHeld[h].append(r)
        resMatch[r] = h
        log(f"{h}'s Hold List: {hosHeld[h][:]}")

        if len(hosHeld[h]) > capacity[h]:
            worst = worstHeld(h, hosHeld[h], rank)
            hosHeld[h].remove(worst)
            resMatch[worst] = None
            log(f"Reject: {worst} -> {h}, {h}'s Hold List: {hosHeld[h][:]}")

            worstPrefs = resPref.get(worst, [])
            if nextChoice[worst] < len(worstPrefs):
                free.append(worst)
                log(f"Requeue Kicked: {worst}, Next Choice Index: {nextChoice[worst]}")
            else:
                log(f"Exhausted Kicked: {worst}")

    hosMatch: HospitalMatch = {h: set(rs) for h, rs in hosHeld.items()}

    elapsed = (time.perf_counter() - start) * 1000
    log(f"FINISH, Elapsed: {elapsed:.2f} ms")

    if returnEvents:
        return resMatch, hosMatch, events
    return resMatch, hosMatch

# Auto Mode
# Build hospital preference lists based on constraints
def generateHosPref(
    resInfo: ResidentsInfoMap,
    hosCriteria: HospitalsCriteriaMap) -> HospitalPreferences:

    allResidents = list(resInfo.keys())
    hosPref: HospitalPreferences = {}

    for h, crit in hosCriteria.items():
        prefDeg = crit.get("prefDeg", [])

        def degreeMatch(r: str) -> int:
            deg = resInfo.get(r, {}).get("degree", None)
            return 1 if deg in prefDeg else 0

        def gpaVal(r: str) -> float:
            g = resInfo.get(r, {}).get("gpa", 0.0)
            try:
                return float(g)
            except Exception:
                return 0.0

        candidates = allResidents
        candidates = [r for r in allResidents if degreeMatch(r) == 1]

        # Sort by: degree match (1 first), GPA (high first)
        candidatesSorted = sorted(
            candidates,
            key=lambda r: (-degreeMatch(r), -gpaVal(r), r)
        )

        hosPref[h] = candidatesSorted

    return hosPref

def stableMatchWithConst(resPref, resInfo, hosCriteria, capacity, returnEvents=False):
    hosPref = generateHosPref(resInfo, hosCriteria)
    return stableMatch(resPref, hosPref, capacity, returnEvents=returnEvents)
