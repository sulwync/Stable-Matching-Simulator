from typing import Dict, List, Set, Tuple, Any, Optional

def explainUnmatched(
    mode: str,
    resPref: Dict[str, List[str]],
    resMatch: Dict[str, Optional[str]],
    hosMatch: Dict[str, Set[str]],
    *,
    # For AUTO (strict degree + GPA)
    resInfo: Optional[Dict[str, Dict[str, Any]]] = None,
    hosCriteria: Optional[Dict[str, Dict[str, Any]]] = None,
    # For MANUAL
    hosPref: Optional[Dict[str, List[str]]] = None,
) -> List[Tuple[str, str]]:

    def resKey(r: str) -> int:
        return int(r[1:]) if len(r) > 1 and r[1:].isdigit() else 10**9

    # Collect unmatched residents from resMatch
    unmatchedResidents = [r for r, h in resMatch.items() if h is None]
    unmatchedResidents.sort(key=resKey)

    if mode.lower() == "auto":
        if resInfo is None or hosCriteria is None:
            raise ValueError("Auto mode explanation requires resInfo and hosCriteria.")
        cutoffAuto = buildCutoffAuto(resInfo, hosMatch)
        return explainAutoStrict(unmatchedResidents, resPref, resInfo, hosCriteria, cutoffAuto)

    # Manual
    if hosPref is None:
        raise ValueError("Manual mode explanation requires hosPref.")
    rank = buildRank(hosPref)
    cutoffManual = buildCutoffManual(rank, hosMatch)
    return explainManual(unmatchedResidents, resPref, rank, hosMatch, cutoffManual)


def buildRank(hosPref: Dict[str, List[str]]) -> Dict[str, Dict[str, int]]:
    return {h: {r: i for i, r in enumerate(prefs)} for h, prefs in hosPref.items()}

def buildCutoffAuto(
    resInfo: Dict[str, Dict[str, Any]],
    hosMatch: Dict[str, Set[str]],
) -> Dict[str, Optional[Tuple[float, str]]]:
    
    cutoff: Dict[str, Optional[Tuple[float, str]]] = {}

    for h, rs in hosMatch.items():
        if not rs:
            cutoff[h] = None
            continue

        worstGPA: Optional[float] = None
        worstId: Optional[str] = None

        for r in rs:
            gpa = float(resInfo.get(r, {}).get("gpa", 0.0))
            if worstGPA is None:
                worstGPA, worstId = gpa, r
            else:
                # worst = lower GPA; tie => lexicographically larger id is "worse"
                if gpa < worstGPA or (gpa == worstGPA and r > worstId):
                    worstGPA, worstId = gpa, r

        cutoff[h] = (worstGPA, worstId)

    return cutoff

def explainAutoStrict(
    unmatchedResidents: List[str],
    resPref: Dict[str, List[str]],
    resInfo: Dict[str, Dict[str, Any]],
    hosCriteria: Dict[str, Dict[str, Any]],
    cutoffAuto: Dict[str, Optional[Tuple[float, str]]],
) -> List[Tuple[str, Dict[str, Any]]]:
    out: List[Tuple[str, Dict[str, Any]]] = []

    for r in unmatchedResidents:
        degree = resInfo.get(r, {}).get("degree", None)
        gpa = float(resInfo.get(r, {}).get("gpa", 0.0))
        prefs = resPref.get(r, [])

        eligible: List[str] = []
        ineligible: List[str] = []

        for h in prefs:
            prefDeg = hosCriteria.get(h, {}).get("prefDeg", [])
            if degree in prefDeg:
                eligible.append(h)
            else:
                ineligible.append(h)

        if not eligible:
            out.append((
                r,
                {
                    "mode": "Auto",
                    "degree": degree,
                    "gpa": gpa,
                    "ineligible": ineligible,
                    "eligible": [],
                    "closestMiss": None,
                    "blocked": [],
                    "note": "No eligible hospitals in preference list (strict degree filter)."
                }
            ))
            continue

        blocked: List[str] = []
        closestH: Optional[str] = None
        closestGap: Optional[float] = None
        closestCut: Optional[Tuple[float, str]] = None

        for h in eligible:
            cut = cutoffAuto.get(h, None)
            if cut is None:
                continue

            worstGPA, worstId = cut
            gap = worstGPA - gpa

            if gap > 0:
                blocked.append(h)
                if closestGap is None or gap < closestGap:
                    closestGap = gap
                    closestH = h
                    closestCut = cut

        closestMiss = None
        if closestH is not None and closestCut is not None and closestGap is not None:
            worstGPA, worstId = closestCut
            closestMiss = f"{closestH} cutoff {worstGPA:.2f} (held by {worstId}); gap {closestGap:.2f}"

        note = None
        if not blocked:
            note = "Eligible hospitals exist and cutoff doesn't strictly block you; proposal path/ordering may explain mismatch."

        out.append((
            r,
            {
                "mode": "Auto",
                "degree": degree,
                "gpa": gpa,
                "ineligible": ineligible,
                "eligible": eligible,
                "closestMiss": closestMiss,
                "blocked": blocked,
                "note": note
            }
        ))

    return out

def buildCutoffManual(
    rank: Dict[str, Dict[str, int]],
    hosMatch: Dict[str, Set[str]],
) -> Dict[str, Optional[Tuple[int, str]]]:
    
    cutoff: Dict[str, Optional[Tuple[int, str]]] = {}

    for h, rs in hosMatch.items():
        if not rs:
            cutoff[h] = None
            continue

        worstRankIndex: Optional[int] = None
        worstId: Optional[str] = None

        for r in rs:
            if r not in rank.get(h, {}):
                continue
            rRank = rank[h][r]
            if worstRankIndex is None:
                worstRankIndex, worstId = rRank, r
            else:
                if rRank > worstRankIndex or (rRank == worstRankIndex and r > worstId):
                    worstRankIndex, worstId = rRank, r

        if worstRankIndex is None or worstId is None:
            cutoff[h] = None
        else:
            cutoff[h] = (worstRankIndex, worstId)

    return cutoff

def explainManual(
    unmatchedResidents: List[str],
    resPref: Dict[str, List[str]],
    rank: Dict[str, Dict[str, int]],
    hosMatch: Dict[str, Set[str]],
    cutoffManual: Dict[str, Optional[Tuple[int, str]]],
) -> List[Tuple[str, Dict[str, Any]]]:
    out: List[Tuple[str, Dict[str, Any]]] = []

    for r in unmatchedResidents:
        prefs = resPref.get(r, [])

        rankedHospitals: List[str] = []
        unrankedHospitals: List[str] = []

        for h in prefs:
            if r in rank.get(h, {}):
                rankedHospitals.append(h)
            else:
                unrankedHospitals.append(h)

        if not rankedHospitals:
            out.append((
                r,
                {
                    "mode": "Manual",
                    "ranked": [],
                    "unranked": unrankedHospitals,
                    "closestMiss": None,
                    "blocked": [],
                    "note": "Resident is unranked by every hospital in their preference list."
                }
            ))
            continue

        blocked: List[str] = []
        closestH: Optional[str] = None
        closestDelta: Optional[int] = None
        closestCut: Optional[Tuple[int, str]] = None

        for h in rankedHospitals:
            cut = cutoffManual.get(h, None)
            if cut is None:
                continue

            worstRankIndex, worstId = cut
            myRankIndex = rank[h][r]

            if myRankIndex > worstRankIndex:
                blocked.append(h)
                delta = myRankIndex - worstRankIndex
                if closestDelta is None or delta < closestDelta:
                    closestDelta = delta
                    closestH = h
                    closestCut = cut

        closestMiss = None
        if closestH is not None and closestCut is not None and closestDelta is not None:
            worstRankIndex, worstId = closestCut
            closestMiss = (
                f"{closestH} cutoff rank={worstRankIndex+1} (held by {worstId}); "
                f"your rank={rank[closestH][r]+1}; delta={closestDelta}"
            )

        note = None
        if not blocked:
            note = "Ranked hospitals exist and cutoff doesn't strictly block you; proposal path/ordering may explain mismatch."

        out.append((
            r,
            {
                "mode": "Manual",
                "ranked": rankedHospitals,
                "unranked": unrankedHospitals,
                "closestMiss": closestMiss,
                "blocked": blocked,
                "note": note
            }
        ))

    return out