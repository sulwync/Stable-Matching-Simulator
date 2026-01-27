from gale_shapley import stableMatch
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

def printOutput(resMatch, hosMatch, resPref, hosPref, capacity):
    print("\n======== Output ========")
    print("Resident -> Hospital:")
    for r in sorted(resMatch.keys()):
        print(f" {r}: {resMatch[r]}")

    print("\nHospital -> Residents:")
    for h in sorted(hosMatch.keys()):
        print(f" {h}: {sorted(list(hosMatch[h]))}")

    m = metrics(resPref, hosPref, capacity, resMatch, hosMatch)

    print("\n======== Metrics ========")
    print(f"Unmatched rate: {m['Unmatched Rate']*100:.1f}%")
    print(f"Average Resident's Preference Rank: {m['Average Resident\'s Preference Rank']:.2f}")
    print(f"Average Hospital's Preference Rank: {m['Average Hospital\'s Preference Rank']:.2f}")
    print(f"({len(m['Blocking Pairs'])}) Blocking pairs: {m['Blocking Pairs']}")

def main():
    # Resident Preferences
    resPref = {
    "R1":  ["H1", "H2", "H3"],
    "R2":  ["H1", "H3"],
    "R3":  ["H2", "H1", "H4"],
    "R4":  ["H2"],                 # single choice
    "R5":  ["H3", "H1"],
    "R6":  ["H1", "H2", "H5"],     # H5 has 0 capacity
    "R7":  ["H4", "H2", "H3"],
    "R8":  ["H3", "H2"],
    "R9":  ["H2", "H4"],
    "R10": ["H1", "H4"],
    "R11": ["H99", "H1"],          # unknown hospital first -> should get rejected then try H1
    "R12": [],                     # no preferences (edge case)
    }

    # Hospital Preferences
    hosPref = {
    "H1": ["R10", "R2", "R1", "R6", "R5", "R11"],
    "H2": ["R3", "R9", "R4", "R1", "R8"],
    "H3": ["R5", "R8", "R7", "R1", "R2"],
    "H4": ["R7", "R9", "R10", "R3"],
    "H5": ["R6", "R1", "R3", "R2"],
    }

    # Hospital Capacities
    capacity = { "H1": 2, "H2": 2, "H3": 1, "H4": 1, "H5": 0 }

    printInput(resPref, hosPref, capacity)

    resMatch, hosMatch, events, elapsed = stableMatch(resPref, hosPref, capacity, returnEvents=True)

    print(f"\nTime taken: {elapsed:.2f} seconds")

    print("\n======== Log (events) ========")
    for e in events:
        print(e)

    printOutput(resMatch, hosMatch, resPref, hosPref, capacity)


if __name__ == "__main__":
    main()



