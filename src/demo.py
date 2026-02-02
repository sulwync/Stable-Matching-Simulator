from gale_shapley import stableMatch, stableMatchWithConst, generateHosPref
from metrics import metrics

def printInput(resPref, hosPref, capacity):
    print("======== Inputs ========")
    print("Resident Preferences:")
    for r, pref in resPref.items():
        print(f" {r}: {pref}")
    print("\nHospital Preferences:")
    for h, pref in hosPref.items():
        print(f" {h}: {pref}")
    print("\nHospital Capacities:", capacity)

def printOutput(resMatch, hosMatch, resPref, hosPref, capacity, events, mode):
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



def main():
    resInfo = {
        "R1":  {"degree": "UG", "gpa": 3.92},
        "R2":  {"degree": "PG", "gpa": 3.75},
        "R3":  {"degree": "UG", "gpa": 3.48},
        "R4":  {"degree": "PG", "gpa": 3.33},
        "R5":  {"degree": "UG", "gpa": 3.67},
        "R6":  {"degree": "PG", "gpa": 3.90},
        "R7":  {"degree": "UG", "gpa": 3.12},
        "R8":  {"degree": "PG", "gpa": 3.58},
        "R9":  {"degree": "UG", "gpa": 3.81},
        "R10": {"degree": "PG", "gpa": 3.05},
        "R11": {"degree": "UG", "gpa": 3.27},
        "R12": {"degree": "PG", "gpa": 3.62},
    }

    # Resident preferences
    resPref = {
        "R1":  ["H1", "H3", "H2", "H4"],
        "R2":  ["H2", "H1", "H4", "H3"],
        "R3":  ["H3", "H2", "H1", "H4"],
        "R4":  ["H1", "H4", "H2", "H3"],
        "R5":  ["H2", "H3", "H4", "H1"],
        "R6":  ["H4", "H1", "H2", "H3"],
        "R7":  ["H3", "H4", "H1", "H2"],
        "R8":  ["H1", "H2", "H3", "H4"],
        "R9":  ["H2", "H4", "H3", "H1"],
        "R10": ["H4", "H3", "H2", "H1"],
        "R11": ["H3", "H1", "H4", "H2"],
        "R12": ["H2", "H1", "H3", "H4"],
    }

    # Manual hospital preferences
    hosPref = {
        "H1": ["R6", "R1", "R9", "R2", "R12", "R5", "R8", "R3", "R4", "R11", "R7", "R10"],
        "H2": ["R1", "R2", "R6", "R9", "R12", "R5", "R8", "R3", "R4", "R11", "R7", "R10"],
        "H3": ["R9", "R5", "R1", "R3", "R12", "R6", "R8", "R2", "R11", "R4", "R7", "R10"],
        "H4": ["R6", "R12", "R2", "R8", "R1", "R9", "R5", "R3", "R4", "R11", "R7", "R10"],
    }

    # Hospital criteria for constraints-generated preferences
    hosCriteria = {
        "H1": {"prefDeg": ["PG"]},
        "H2": {"prefDeg": ["UG"]},
        "H3": {"prefDeg": ["UG", "PG"]},
        "H4": {"prefDeg": ["PG", "UG"]},
    }

    # Hospital capacities
    capacity = {
        "H1": 3,
        "H2": 3,
        "H3": 2,
        "H4": 2,
    }

    mode = "Manual" 

    if mode == "Manual":
        usedHosPref = hosPref
        printInput(resPref, hosPref, capacity)
        resMatch, hosMatch, events, elapsed = stableMatch(resPref, hosPref, capacity, True)
    else:
        usedHosPref = generateHosPref(resInfo, hosCriteria)
        printInput(resPref, usedHosPref, capacity)
        resMatch, hosMatch, events, elapsed = stableMatchWithConst(
            resPref, resInfo, hosCriteria, capacity, returnEvents=True
        )

    print(f"\nTime taken: {elapsed:.2f} seconds")

    print("\n======== Log (events) ========")
    for e in events:
        print(e)

    printOutput(resMatch, hosMatch, resPref, usedHosPref, capacity, events, mode)

if __name__ == "__main__":
    main()



