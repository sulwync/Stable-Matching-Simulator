from __future__ import annotations

from collections import deque
import time
from typing import Any, Literal

from core.types import (
    ResidentId, HospitalId, ResidentPreferences, HospitalPreferences, CapacityMap,
    RankTable, ResidentMatch, HospitalMatch, HospitalHeld, EventLog, FreeQueue, 
    ResidentsInfoMap, HospitalsCriteriaMap, StableMatchReturn,
)

EventMode = Literal["text", "json"]

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
        returnEvents: bool=False,
        eventMode: EventMode="text",
        includeQueueSnapshot: bool=False) -> StableMatchReturn:

    start = time.perf_counter()
    rank = buildRank(hosPref)

    events: EventLog = []
    step = 0 

    # Initialize state
    resident: list[ResidentId] = list(resPref.keys())
    hospital: list[HospitalId] = list(hosPref.keys())

    nextChoice: dict[ResidentId, int] = {r: 0 for r in resident}
    resMatch: ResidentMatch = {r: None for r in resident}
    hosHeld: HospitalHeld = {h: [] for h in hospital}

    free: FreeQueue = deque([r for r in resident if len(resPref.get(r, [])) > 0])

    def log_text(line: str) -> None:
        if returnEvents:
            events.append(line)

    def log_json(payload: dict[str, Any]) -> None:
        nonlocal step
        if not returnEvents:
            return
        payload["t"] = step
        step += 1
        if includeQueueSnapshot:
            payload["free"] = list(free)
        events.append(payload)

    def log(line_or_payload: Any) -> None:
        if not returnEvents:
            return
        if eventMode == "json":
            # Require dicts in json mode
            if isinstance(line_or_payload, dict):
                log_json(line_or_payload)
            else:
                # Safety: allow accidental string by wrapping
                log_json({"type": "log", "msg": str(line_or_payload)})
        else:
            # text mode (existing behavior)
            log_text(str(line_or_payload))

    # START event
    if eventMode == "json":
        log({
            "type": "start",
            "residents": resident,
            "hospitals": hospital,
            "capacity": dict(capacity),
            "initialFree": list(free)
        })
    else:
        log(f"START: {list(free)}")

    while free:
        r = free.popleft()

        if eventMode == "json":
            log({"type": "pop_free", "r": r})
        else:
            log(f"Resident Selected: {r}, Queue: {list(free)}")

        if resMatch[r] is not None:
            if eventMode == "json":
                log({"type": "skip_already_matched", "r": r, "h": resMatch[r]})
            continue

        prefs = resPref.get(r, [])
        if nextChoice[r] >= len(prefs):
            if eventMode == "json":
                log({"type": "exhausted", "r": r})
            else:
                log(f"Exhausted: {r}")
            continue  # no more hospitals to propose to

        h = prefs[nextChoice[r]]

        if eventMode == "json":
            log({"type": "proposal", "r": r, "h": h, "choiceIndex": nextChoice[r]})
        else:
            log(f"Proposal: {r} -> {h}, Preference Index: {nextChoice[r]}")

        nextChoice[r] += 1

        # Reject if invalid hospital or no capacity
        if h not in capacity or capacity[h] <= 0 or h not in hosHeld:
            if eventMode == "json":
                log({"type": "reject", "r": r, "h": h, "reason": "invalid_or_no_capacity"})
            else:
                log(f"Reject: {r}, No Capacity or Invalid: {h}")

            if nextChoice[r] < len(prefs):
                free.append(r)
                if eventMode == "json":
                    log({"type": "requeue", "r": r, "reason": "try_next_choice", "nextChoice": nextChoice[r]})
                else:
                    log(f"Requeue: {r}, Next Choice Index: {nextChoice[r]}")
            else:
                if eventMode == "json":
                    log({"type": "exhausted", "r": r, "reason": "after_reject"})
                else:
                    log(f"Exhausted After Reject: {r}")
            continue

        # Reject if hospital does not rank resident
        if r not in rank.get(h, {}):
            if eventMode == "json":
                log({"type": "reject", "r": r, "h": h, "reason": "unranked"})
            else:
                log(f"Reject Unranked: {r} -> {h}")

            if nextChoice[r] < len(prefs):
                free.append(r)
                if eventMode == "json":
                    log({"type": "requeue", "r": r, "reason": "unranked_try_next", "nextChoice": nextChoice[r]})
                else:
                    log(f"Requeue Unranked: {r}, Next Choice Index: {nextChoice[r]}")
            else:
                if eventMode == "json":
                    log({"type": "exhausted", "r": r, "reason": "after_unranked_reject"})
                else:
                    log(f"Exhausted After Unranked Reject: {r}")
            continue

        # Tentatively hold
        hosHeld[h].append(r)
        resMatch[r] = h

        if eventMode == "json":
            log({"type": "hold_add", "h": h, "r": r, "heldSize": len(hosHeld[h]), "capacity": capacity.get(h, 0)})
        else:
            log(f"{h}'s Hold List: {hosHeld[h][:]}")

        # Over capacity -> kick worst
        if len(hosHeld[h]) > capacity[h]:
            worst = worstHeld(h, hosHeld[h], rank)
            hosHeld[h].remove(worst)
            resMatch[worst] = None

            if eventMode == "json":
                log({"type": "kick", "h": h, "kicked": worst, "kept": hosHeld[h][:]})
            else:
                log(f"Reject: {worst} -> {h}, {h}'s Hold List: {hosHeld[h][:]}")

            worstPrefs = resPref.get(worst, [])
            if nextChoice[worst] < len(worstPrefs):
                free.append(worst)
                if eventMode == "json":
                    log({"type": "requeue", "r": worst, "reason": "kicked", "nextChoice": nextChoice[worst]})
                else:
                    log(f"Requeue Kicked: {worst}, Next Choice Index: {nextChoice[worst]}")
            else:
                if eventMode == "json":
                    log({"type": "exhausted", "r": worst, "reason": "kicked_no_more_choices"})
                else:
                    log(f"Exhausted Kicked: {worst}")

    hosMatch: HospitalMatch = {h: set(rs) for h, rs in hosHeld.items()}

    elapsed = (time.perf_counter() - start) * 1000

    if eventMode == "json":
        log({"type": "finish", "elapsedMs": round(elapsed, 2)})
    else:
        log(f"FINISH, Elapsed: {elapsed:.2f} ms")

    if returnEvents:
        return resMatch, hosMatch, events
    return resMatch, hosMatch

def generateHosPref(
    resInfo: ResidentsInfoMap,
    hosCriteria: HospitalsCriteriaMap
):
    allResidents = list(resInfo.keys())
    hosPref: HospitalPreferences = {}

    for h, crit in hosCriteria.items():
        prefDeg = crit.get("prefDeg", [])

        def degreeMatch(r: str) -> int:
            if "All" in prefDeg:
                return 1
            deg = resInfo.get(r, {}).get("degree", None)
            return 1 if deg in prefDeg else 0

        def gpaVal(r: str) -> float:
            g = resInfo.get(r, {}).get("gpa", 0.0)
            try:
                return float(g)
            except Exception:
                return 0.0
        candidates = [r for r in allResidents if degreeMatch(r) == 1]
        candidatesSorted = sorted(
            candidates,
            key=lambda r: (-degreeMatch(r), -gpaVal(r), r)
        )

        hosPref[h] = candidatesSorted

    return hosPref


def stableMatchWithConst(resPref, resInfo, hosCriteria, capacity, returnEvents=False, **kwargs):
    hosPref = generateHosPref(resInfo, hosCriteria)
    return stableMatch(resPref, hosPref, capacity, returnEvents=returnEvents, **kwargs)