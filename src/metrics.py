from typing import Dict, List, Set, Optional, Any, Tuple
from gale_shapley import buildRank

def metrics(
        resPref: Dict[str, List[str]], 
        hosPref: Dict[str, List[str]],
        capacity: Dict[str, int], 
        resMatch: Dict[str, Optional[str]], 
        hosMatch: Dict[str, Set[str]],
        events: Optional[List[str]] = None) -> Dict[str, Any]:

    rank = buildRank(hosPref)

    # Total proposals made
    totalProposals = 0
    if events is not None:
        totalProposals = sum(1 for e in events if e.startswith("Proposal:"))

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

    # Blocking Pairs
    def resPrefers(r: str, h: str) -> bool:
        prefs = resPref.get(r, [])
        if h not in prefs:
            return False
        
        current = resMatch.get(r, None)
        if current is None:
            return True
        
        return prefs.index(h) < prefs.index(current)
    
    def hosPrefers(r: str, h: str) -> bool:
        if h not in capacity or capacity[h] <= 0:
            return False
        
        if r not in rank.get(h, {}):
            return False
        
        held = hosMatch.get(h, set())

        if len(held) < capacity[h]:
            return True
        
        worstRank = -1
        for x in held:
            xRank = rank[h][x]
            if xRank > worstRank:
                worstRank = xRank
        return rank[h][r] < worstRank
    
    blockingPairs: List[Tuple[str, str]] = []
    for r, prefs in resPref.items():
        for h in prefs:
            if resMatch.get(r) == h:
                continue
            if resPrefers(r, h) and hosPrefers(r, h):
                blockingPairs.append((r, h))

    # First choice rate (residents)
    matchedResidents = [r for r, h in resMatch.items() if h is not None]
    firstChoiceCount = 0
    for r in matchedResidents:
        h = resMatch[r]
        prefs = resPref.get(r, [])
        if prefs and h == prefs[0]:
            firstChoiceCount += 1

    firstChoiceRate = (firstChoiceCount / len(matchedResidents)) if matchedResidents else 0.0


    return { "Unmatched Rate": unmatchedRate, 
            "Average Resident's Preference Rank": avgResRank,
            "Average Hospital's Preference Rank": avgHosRank, 
            "Blocking Pairs": blockingPairs,
            "First Choice Rate": firstChoiceRate,
            "First Choice Count": firstChoiceCount,
            "Total Proposals": totalProposals,}