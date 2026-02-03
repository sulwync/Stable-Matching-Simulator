from core.gale_shapley import stableMatch, stableMatchWithConst, generateHosPref
from core.explain_unmatched import explainUnmatched
from core.metrics import metrics

def printInput(resPref, hosPref, capacity):
    print("======== Inputs ========")
    print("Resident Preferences:")
    for r, pref in resPref.items():
        print(f" {r}: {pref}")
    print("\nHospital Preferences:")
    for h, pref in hosPref.items():
        print(f" {h}: {pref}")
    print("\nHospital Capacities:", capacity)

def printOutput(resMatch, hosMatch, resPref, hosPref, capacity, events, mode, resInfo, hosCriteria):
    print("\n======== Output ========")
    print(f"Mode: {mode}")
    print("Resident -> Hospital:")
    def resKey(r: str) -> int:
        return int(r[1:])
    
    for r in sorted(resMatch.keys(), key=resKey):
        print(f" {r}: {resMatch[r]}")

    print("\nHospital -> Residents:")
    for h in sorted(hosMatch.keys(), key=resKey):
        print(f" {h}: {sorted(list(hosMatch[h]))}")

    m = metrics(resPref, hosPref, capacity, resMatch, hosMatch, events)

    print("\n======== Metrics ========")
    print(f"Total proposals: {m['Total Proposals']}")
    print(f"Unmatched rate: {m['Unmatched Rate']*100:.1f}%")
    print(f"Max proposals by a single resident: {m['Max Proposals By A Resident'][0]} ({m['Max Proposals By A Resident'][1]} proposals)")
    print(f"Average Resident's Preference Rank: {m['Average Resident\'s Preference Rank']:.2f}")
    print(f"Average Hospital's Preference Rank: {m['Average Hospital\'s Preference Rank']:.2f}")
    print(f"First choice rate: {m['First Choice Rate']*100:.1f}% "
      f"({m['First Choice Count']} residents)")
    print(f"{len(m['Blocking Pairs'])} Blocking pairs: {m['Blocking Pairs']}")

    explanations = explainUnmatched(
        mode=mode,
        resPref=resPref,
        resMatch=resMatch,
        hosMatch=hosMatch,
        resInfo=resInfo,
        hosCriteria=hosCriteria,
        hosPref=hosPref
    )
    
    def printUnmatchedExplanation(explanations):
        print("\n======== Unmatched Explanation ========")
        for r, info in explanations:
            if info.get("mode") == "Auto":
                print(f"  {r}: degree='{info['degree']}', gpa={info['gpa']:.2f}")
                if info.get("ineligible"):
                    print(f"    ineligible (degree mismatch): {info['ineligible']}")
                if info.get("eligible"):
                    print(f"    eligible: {info['eligible']}")
                if info.get("closestMiss"):
                    print(f"    closest miss: {info['closestMiss']}")
                if info.get("blocked"):
                    print(f"    blocked by cutoff at: {info['blocked']}")
                if info.get("note"):
                    print(f"    note: {info['note']}")
            else:
                print(f"  {r}:")
                if info.get("unranked"):
                    print(f"    unranked by: {info['unranked']}")
                if info.get("ranked"):
                    print(f"    ranked by: {info['ranked']}")
                if info.get("closestMiss"):
                    print(f"    closest miss: {info['closestMiss']}")
                if info.get("blocked"):
                    print(f"    blocked at: {info['blocked']}")
                if info.get("note"):
                    print(f"    note: {info['note']}")

    printUnmatchedExplanation(explanations)

def main():
    # Resident Information
    resInfo = {
        "R1": {"degree": "UG", "gpa": 3.95},
        "R2": {"degree": "UG", "gpa": 3.55},
        "R3": {"degree": "UG", "gpa": 2.90},
        "R4": {"degree": "PG", "gpa": 3.85},
        "R5": {"degree": "PG", "gpa": 3.40},
    }

    # Resident Preferences
    resPref = {
        "R1": ["H1", "H2", "H3"],
        "R2": ["H2", "H1", "H3"],
        "R3": ["H2", "H3", "H1"],
        "R4": ["H3", "H2", "H1"],
        "R5": ["H3", "H1", "H2"],
    }

    # Hospital Preferences
    hosPref = {
        "H1": ["R2", "R1", "R5", "R3", "R4"],
        "H2": ["R1", "R2", "R4", "R3", "R5"],
        "H3": ["R4", "R5", "R3", "R2", "R1"],
    }

    # Hospital Capacities
    capacity = { "H1": 1, "H2": 1, "H3": 1}

    # Hospital Criteria
    hosCriteria = {
        "H1": {"prefDeg": ["PG"]},
        "H2": {"prefDeg": ["UG"]},
        "H3": {"prefDeg": ["UG", "PG"]},
    }

    mode = "Manual" 
    if mode == "Manual":
        usedHosPref = hosPref
        printInput(resPref, hosPref, capacity)
        resMatch, hosMatch, events = stableMatch(resPref, hosPref, capacity, True)
    else:
        usedHosPref = generateHosPref(resInfo, hosCriteria)
        printInput(resPref, usedHosPref, capacity)
        resMatch, hosMatch, events = stableMatchWithConst(
            resPref, resInfo, hosCriteria, capacity, returnEvents=True
        )

    print("\n======== Log (events) ========")
    for e in events:
        print(e)

    printOutput(resMatch, hosMatch, resPref, usedHosPref, capacity, events, mode, resInfo, hosCriteria)

if __name__ == "__main__":
    main()



