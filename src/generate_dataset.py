import random
import json
import argparse
from pathlib import Path


def generate_manual_dataset(num_hospitals: int, num_residents: int, seed: int = None) -> dict:
    """Generate a random manual mode dataset."""
    if seed is not None:
        random.seed(seed)
    
    hospitals = []
    residents = []
    
    # Generate hospitals
    for i in range(num_hospitals):
        hospital = {
            "capacity": random.randint(1, 5),
            "preference": []
        }
        hospitals.append(hospital)
    
    # Generate residents
    for i in range(num_residents):
        resident = {
            "preference": []
        }
        residents.append(resident)
    
    # Generate random preferences for hospitals
    for i, hospital in enumerate(hospitals):
        # Each hospital ranks a random subset of residents
        num_prefs = random.randint(1, min(max(3, num_residents // 2), num_residents))
        prefs = random.sample(range(num_residents), num_prefs)
        hospital["preference"] = [f"R{p+1}" for p in sorted(prefs)]
    
    # Generate random preferences for residents
    for i, resident in enumerate(residents):
        # Each resident ranks a random subset of hospitals
        num_prefs = random.randint(1, min(max(2, num_hospitals // 2), num_hospitals))
        prefs = random.sample(range(num_hospitals), num_prefs)
        resident["preference"] = [f"H{p+1}" for p in sorted(prefs)]
    
    return {
        "name": f"Random Manual Dataset ({num_hospitals} hospitals, {num_residents} residents)",
        "mode": "manual",
        "hospitals": hospitals,
        "residents": residents,
    }


def generate_auto_dataset(num_hospitals: int, num_residents: int, seed: int = None) -> dict:
    """Generate a random auto mode dataset."""
    if seed is not None:
        random.seed(seed)
    
    degree_options = ["Undergraduate", "Postgraduate", "All"]
    
    hospitals = []
    residents = []
    
    # Generate hospitals
    for i in range(num_hospitals):
        hospital = {
            "capacity": random.randint(1, 5),
            "pref_degree": random.choice(degree_options)
        }
        hospitals.append(hospital)
    
    # Generate residents
    for i in range(num_residents):
        resident = {
            "gpa": round(random.uniform(2.0, 4.0), 2),
            "degree": random.choice(["Undergraduate", "Postgraduate"]),
            "preference": []
        }
        residents.append(resident)
    
    # Generate random preferences for residents
    for i, resident in enumerate(residents):
        # Each resident ranks a random subset of hospitals
        num_prefs = random.randint(1, min(max(2, num_hospitals // 2), num_hospitals))
        prefs = random.sample(range(num_hospitals), num_prefs)
        resident["preference"] = [f"H{p+1}" for p in sorted(prefs)]
    
    return {
        "name": f"Random Auto Dataset ({num_hospitals} hospitals, {num_residents} residents)",
        "mode": "auto",
        "hospitals": hospitals,
        "residents": residents,
    }

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate random dataset for Stable Matching Simulator"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["manual", "auto"],
        default="manual",
        help="Dataset mode: 'manual' or 'auto' (default: manual)"
    )
    parser.add_argument(
        "--hospitals",
        type=int,
        default=5,
        help="Number of hospitals (default: 5)"
    )
    parser.add_argument(
        "--residents",
        type=int,
        default=10,
        help="Number of residents (default: 10)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (default: random_<mode>_dataset.json)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility (optional)"
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if args.hospitals < 1 or args.residents < 1:
        print("Error: Number of hospitals and residents must be at least 1")
        return
    
    # Generate dataset based on mode
    if args.mode == "manual":
        dataset = generate_manual_dataset(args.hospitals, args.residents, args.seed)
    else:  # auto
        dataset = generate_auto_dataset(args.hospitals, args.residents, args.seed)
    
    # Set default output path if not provided
    output_path = Path(args.output) if args.output else Path(f"random_{args.mode}_dataset.json")
    
    # Save to file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)
    
    print(f"✓ Dataset generated: {output_path}")
    print(f"  - Mode: {args.mode}")
    print(f"  - Hospitals: {args.hospitals}")
    print(f"  - Residents: {args.residents}")
    if args.seed is not None:
        print(f"  - Seed: {args.seed}")
    print(f"\nYou can now import this file in the simulator using 'Import Dataset' button.")


if __name__ == "__main__":
    main()
