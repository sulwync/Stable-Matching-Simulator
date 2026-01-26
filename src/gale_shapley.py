from typing import Dict, List, Optional, Set, Tuple, Any
import time

def stableMatch( resPref: Dict[str, List[str]], hosPref: Dict[str, List[str]],
    capacity: Dict[str, int], returnEvents: bool=False,) -> Tuple[Any, ...]:

    start = time.perf_counter()
    events: List[Tuple[Any, ...]] = []

    def log(line1: str) -> None:
        events.append((line1))

    # Initialize state
    resident = list(resPref.keys())
    hospital = list(hosPref.keys())
    
    nextChoice: Dict[str, int] = {r: 0 for r in resident}
    resMatch: Dict[str, Optional[str]] = {r: None for r in resident}
    hosHeld: Dict[str, List[str]] = {h: [] for h in hospital}

    free: List[str] = [r for r in resident if len(resPref.get(r, [])) > 0]
    log(f"START: {free[:]}")

    def hosRank(h: str, r: str) -> int:
        try:
            return hosPref[h].index(r)
        except ValueError:
            return 10**9 # if not ranked, treat it as worst

    while free:
        r = free.pop(0)
        log(f"Resident Selected: {r}, Queue: {free[:]}")

        prefs = resPref.get(r, [])
        if nextChoice[r] >= len(prefs):
            log(f"Exhausted: {r}")
            continue # no more hospitals to propose to

        h = prefs[nextChoice[r]]
        log(f"Proposal: {r} -> {h}, Preference Index: {nextChoice[r]}")

        nextChoice[r] += 1

        # Reject if invalid hospital or no capacity
        if h not in capacity or capacity[h] <= 0:
            log(f"Reject: {r}, No Capacity or Invalid: {h}")
            if nextChoice[r] < len(prefs):
                free.append(r)
                log(f"Requeue: {r}, Next Choice Index: {nextChoice[r]}")
            else:
                log(f"Exhausted After Reject: {r}")
            continue

        hosHeld[h].append(r)
        resMatch[r] = h
        log(f"{h}'s Hold List: {hosHeld[h][:]}")

        if len(hosHeld[h]) > capacity[h]:
            worst = hosHeld[h][0]
            worstRank = hosRank(h, worst)

            for r in hosHeld[h][1:]:
                rRank = hosRank(h,r)
                if rRank > worstRank:
                    worst = r
                    worstRank = rRank
            
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
