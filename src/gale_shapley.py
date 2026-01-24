from typing import Dict, List, Optional, Set, Tuple

def stableMatch( resPref: Dict[str, List[str]], hosPref: Dict[str, List[str]],
    capacity: Dict[str, int], returnEvents: bool=False,) -> Tuple[Dict[str, Optional[str]], Dict[str, Set[str]]]:
    
    # Initialize state
    resident = list(resPref.keys())
    hospital = list(hosPref.keys())
    
    nextChoice: Dict[str, int] = {r: 0 for r in resident}
    resMatch: Dict[str, Optional[str]] = {r: None for r in resident}
    hosHeld: Dict[str, List[str]] = {h: [] for h in hospital}
    free: List[str] = [r for r in resident if len(resPref.get(r, [])) > 0]

    def hosRank(h: str, r: str) -> int:
        try:
            return hosPref[h].index(r)
        except ValueError:
            return 10**9

    while free:
        r = free.pop(0)

        prefs = resPref.get(r, [])
        if nextChoice[r] >= len(prefs):
            continue # No more hospitals to propose to

        h = prefs[nextChoice[r]]

        if h not in capacity or capacity[h] <= 0:
            nextChoice[r] += 1
            if nextChoice[r] < len(prefs):
                free.append(r)
            continue

        hosHeld[h].append(r)
        resMatch[r] = h

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

            nextChoice[worst] += 1
            if nextChoice[worst] < len(prefs):
                free.append(worst)

        hosMatch: Dict[str, Set[str]] = {h: set(rs) for h, rs in hosHeld.items()}

        return resMatch, hosMatch
