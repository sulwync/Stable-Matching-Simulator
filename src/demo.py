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

def printOutput(resMatch, hosMatch, resPref, hosPref, capacity, events):
    print("\n======== Output ========")
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
    print(f"Average Resident's Preference Rank: {m['Average Resident\'s Preference Rank']:.2f}")
    print(f"Average Hospital's Preference Rank: {m['Average Hospital\'s Preference Rank']:.2f}")
    print(f"{len(m['Blocking Pairs'])} Blocking pairs: {m['Blocking Pairs']}")
    print(f"First choice rate: {m['First Choice Rate']*100:.1f}% "
      f"({m['First Choice Count']} residents)")



def main():
    # Resident Preferences
    resPref = {
        "R1": ["H1", "H2"],
        "R2": ["H2"],
        "R3": ["H2", "H3"],
        "R4": ["H3"],
        "R5": ["H1"],
        "R6": [],
    }


    # Hospital Preferences
    hosPref = {
        "H1": ["R5", "R1"],
        "H2": ["R1", "R3", "R2"],
        "H3": ["R2", "R4"],
    }


    # Hospital Capacities
    capacity = { "H1": 1, "H2": 2, "H3": 1 }

    printInput(resPref, hosPref, capacity)

    resMatch, hosMatch, events, elapsed = stableMatch(resPref, hosPref, capacity, returnEvents=True)

    print(f"\nTime taken: {elapsed:.2f} seconds")

    print("\n======== Log (events) ========")
    for e in events:
        print(e)

    printOutput(resMatch, hosMatch, resPref, hosPref, capacity, events)


if __name__ == "__main__":
    main()



