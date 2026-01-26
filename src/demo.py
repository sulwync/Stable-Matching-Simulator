from gale_shapley import stableMatch

def printInput(resPref, hosPref, capacity):
    print("======== Inputs ========")
    print("Resident Preferences:")
    for r, pref in resPref.items():
        print(f" {r}: {pref}")
    print("\nHospital Preferences:")
    for h, pref in hosPref.items():
        print(f" {h}: {pref}")
    print("\nHospital Capacities:", capacity)

def printOutput(resMatch, hosMatch):
    print("\n======== Output ========")
    print("Resident -> Hospital:")
    for r in sorted(resMatch.keys()):
        print(f" {r}: {resMatch[r]}")

    print("\nHospital -> Residents:")
    for h in sorted(hosMatch.keys()):
        print(f" {h}: {sorted(list(hosMatch[h]))}")

def main():
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
    capacity = { "H1": 1, "H2": 1, "H3": 1 }

    printInput(resPref, hosPref, capacity)

    resMatch, hosMatch, events, elapsed = stableMatch(resPref, hosPref, capacity, returnEvents=True)

    print(f"\nTime taken: {elapsed:.2f} seconds")

    print("\n======== Log (events) ========")
    for e in events:
        print(e)

    printOutput(resMatch, hosMatch)


if __name__ == "__main__":
    main()



