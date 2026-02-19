from typing import Optional

from core.types import (
    ResidentId, HospitalId, ResidentPreferences, HospitalPreferences,
    CapacityMap, ResidentMatch, HospitalMatch, EventLog, MetricsResult, BlockingPairs)

from core.gale_shapley import buildRank

def metrics(
    resPref: ResidentPreferences,
    hosPref: HospitalPreferences,
    capacity: CapacityMap,
    resMatch: ResidentMatch,
    hosMatch: HospitalMatch,
    events: Optional[EventLog] = None) -> MetricsResult:

    rank = buildRank(hosPref)

    # Total proposals made
    totalProposals = 0
    if events is not None:
        totalProposals = sum(1 for e in events if e.startswith("Proposal:"))

    # Unmatched Rate
    total = len(resMatch)
    unmatched = sum(1 for r in resMatch if resMatch[r] is None)
    unmatchedRate = unmatched / total if total > 0 else 0.0

    # Max proposals by a single resident (unluckiest resident)
    proposalsByRes: dict[ResidentId, int] = {r: 0 for r in resPref.keys()}
    unluckiestCount = 0

    if events is not None:
        for e in events:
            if e.startswith("Proposal:"):
                parts = e.split()
                if len(parts) >= 2:
                    r = parts[1]
                    proposalsByRes[r] = proposalsByRes.get(r, 0) + 1

        for r, k in proposalsByRes.items():
            if k > unluckiestCount:
                unluckiestCount = k
                unluckiestRes = r
        
        maxCount = 0
        for r in proposalsByRes:
            if proposalsByRes[r] > maxCount:
                maxCount = proposalsByRes[r]

        unluckiestRes = []
        for r in proposalsByRes:
            if proposalsByRes[r] == maxCount and maxCount > 0:
                unluckiestRes.append(r)

        unluckiestRes.sort()


    # Average Resident's Preference Rank
    resRanks: list[int] = []
    for r, h in resMatch.items():
        if h is None: 
            continue
        prefs = resPref.get(r, [])
        if h in prefs:
            resRanks.append(prefs.index(h) + 1)
    avgResRank = (sum(resRanks) / len(resRanks)) if resRanks else 0.0

    # Average Hospital's Preference Rank
    hosRanks: list[int] = []
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
    
    def hosPrefers(r: ResidentId, h: HospitalId) -> bool:
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
    
    blockingPairs: BlockingPairs = []
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
            "Total Proposals": totalProposals,
            "Max Proposals By A Resident": (unluckiestRes, unluckiestCount),
        }