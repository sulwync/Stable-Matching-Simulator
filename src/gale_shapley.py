from typing import Dict, List, Optional, Set, Tuple, Any, Literal
import time

UnrankedPolicy = Literal["reject", "worst"]

def buildRank(hosPref: Dict[str, List[str]]) -> Dict[str, Dict[str, int]]:
    return {h: {r: i for i, r in enumerate(prefs)} for h, prefs in hosPref.items()}

def worstHeld(h: str, held: List[str], rank: Dict[str, Dict[str, int]]) -> str:
    worst = held[0]
    worstRank = rank.get(h, {}).get(worst, 10**9)
    for r in held[1:]:
        rRank = rank.get(h, {}).get(r, 10**9)
        if rRank > worstRank:
            worst, worstRank = r, rRank
    return worst

def stableMatch( 
        resPref: Dict[str, List[str]], hosPref: Dict[str, List[str]], 
        capacity: Dict[str, int], returnEvents: bool=False, 
        unrankedPolicy: UnrankedPolicy = "worst") -> Tuple[Any, ...]:

    start = time.perf_counter()
    rank = buildRank(hosPref)
    events: List[str] = []

    def log(line: str) -> None:
        if returnEvents:
            events.append((line))

    # Initialize state
    resident = list(resPref.keys())
    hospital = list(hosPref.keys())
    
    nextChoice: Dict[str, int] = {r: 0 for r in resident}
    resMatch: Dict[str, Optional[str]] = {r: None for r in resident}
    hosHeld: Dict[str, List[str]] = {h: [] for h in hospital}

    free: List[str] = [r for r in resident if len(resPref.get(r, [])) > 0]
    log(f"START: {free[:]}")

    def acceptable(h: str, r: str) -> bool:
        if unrankedPolicy == "reject":
            return r in rank.get(h, {})
        return True

    while free:
        r = free.pop(0)
        log(f"Resident Selected: {r}, Queue: {free[:]}")

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

        if not acceptable(h, r):
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
    log(f"FINISH, Elapsed Seconds: {elapsed:.2f} ms")

    if returnEvents:
        return resMatch, hosMatch, events, elapsed
    return resMatch, hosMatch
