from collections import deque
from typing import Dict, List, Optional, Set, Tuple, Any, Literal, Deque
import time

def buildRank(hosPref: Dict[str, List[str]]) -> Dict[str, Dict[str, int]]:
    return {h: {r: i for i, r in enumerate(prefs)} for h, prefs in hosPref.items()}

def worstHeld(h: str, held: List[str], rank: Dict[str, Dict[str, int]]) -> str:
    worst = held[0]
    worstRank = rank[h][worst]
    for r in held[1:]:
        rRank = rank[h][r]
        if rRank > worstRank:
            worst, worstRank = r, rRank
    return worst

def stableMatch( 
        resPref: Dict[str, List[str]], 
        hosPref: Dict[str, List[str]], 
        capacity: Dict[str, int], 
        returnEvents: bool=False) -> Tuple[Any, ...]:

    start = time.perf_counter()
    rank = buildRank(hosPref)
    events: List[str] = []

    def log(line: str) -> None:
        if returnEvents:
            events.append(line)

    # Initialize state
    resident = list(resPref.keys())
    hospital = list(hosPref.keys())
    
    nextChoice: Dict[str, int] = {r: 0 for r in resident}
    resMatch: Dict[str, Optional[str]] = {r: None for r in resident}
    hosHeld: Dict[str, List[str]] = {h: [] for h in hospital}

    free: Deque[str] = deque([r for r in resident if len(resPref.get(r, [])) > 0])
    log(f"START: {free}")

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

    hosMatch: Dict[str, Set[str]] = {h: set(rs) for h, rs in hosHeld.items()}

    elapsed = (time.perf_counter() - start) * 1000
    log(f"FINISH, Elapsed: {elapsed:.2f} ms")

    if returnEvents:
        return resMatch, hosMatch, events, elapsed
    return resMatch, hosMatch

def metrics(
        resPref: Dict[str, List[str]], 
        hosPref: Dict[str, List[str]],
        capacity: Dict[str, int], 
        resMatch: Dict[str, Optional[str]], 
        hosMatch: Dict[str, Set[str]],) -> Dict[str, Any]:

    rank = buildRank(hosPref)

    # Unmatched Rate
    total = len(resMatch)
    unmatched = sum(1 for r in resMatch if resMatch[r] is None)
    unmatchedRate = unmatched / total if total > 0 else 0.0

    # Average Resident's Preference Rank
    resRanks: List[int] = []
    for r, h in resMatch.items():
        if h is None: 
            continue
        prefs = resPref.get(r, [])
        if h in prefs:
            resRanks.append(prefs.index(h) + 1)
    avgResRank = (sum(resRanks) / len(resRanks)) if resRanks else 0.0

    # Average Hospital's Preference Rank
    hosRanks: List[int] = []
    for h, rs in hosMatch.items():
        for r in rs:
            if r in rank.get(h, {}):
                hosRanks.append(rank[h][r] + 1)
            else:
                pass
    avgHosRank = (sum(hosRanks) / len(hosRanks)) if hosRanks else 0.0

    return { "Unmatched Rate": unmatchedRate, "Average Resident's Preference Rank": avgResRank,
            "Average Hospital's Preference Rank": avgHosRank }