from gale_shapley import stable_matching

def printInput(resPref, hosPref, capacity):
    print("======== Inputs ========")
    print("Resident Preferences:")
    for r, pref in resPref.items():
        print(f" {r}: {pref}")
    print("\nHospital Preferences:")
    for h, pref in hosPref.items():
        print(f" {h}: {pref}")
    print("\nHospital Capacities:", capacity)

def main():
    # Resident Preferences
    resPref = {
        "R1": ["H1", "H2"],
        "R2": ["H2", "H1"],
        "R3": ["H2", "H1"],
    }

    # Hospital Preferences
    hosPref = {
        "H1": ["R2", "R1", "R3"],
        "H2": ["R1", "R2", "R3"],
    }

    # Hospital Capacities
    capacity = { "H1": 2, "H2": 1 }

    printInput(resPref, hosPref, capacity)