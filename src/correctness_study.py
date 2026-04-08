from __future__ import annotations

import argparse
import csv
from pathlib import Path
from statistics import mean

from core.gale_shapley import stableMatch, generateHosPref
from core.metrics import metrics
from dataset_utils import load_dataset, group_datasets_by_size, dataset_to_manual_inputs, dataset_to_auto_inputs


BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset" / "runtime"
RESULTS_DIR = BASE_DIR / "results" / "correctness"


def check_correctness(dataset: dict) -> dict:
    mode = dataset["mode"]

    if mode == "manual":
        res_pref, hos_pref, capacity = dataset_to_manual_inputs(dataset)
        res_match, hos_match = stableMatch(res_pref, hos_pref, capacity)
    else:
        res_pref, res_info, hos_criteria, capacity = dataset_to_auto_inputs(dataset)
        hos_pref = generateHosPref(res_info, hos_criteria)
        res_match, hos_match = stableMatch(res_pref, hos_pref, capacity)

    # Compute metrics for blocking pairs
    mets = metrics(res_pref, hos_pref, capacity, res_match, hos_match)
    blocking_pairs = mets["Blocking Pairs"]

    # Capacity violations: hospitals with more residents than capacity
    cap_violations = sum(1 for h, rs in hos_match.items() if len(rs) > capacity[h])

    # Invalid matches: matches where resident didn't prefer hospital or hospital didn't rank resident
    invalid_matches = 0
    for r, h in res_match.items():
        if h is not None:
            if h not in res_pref.get(r, []):
                invalid_matches += 1
            if r not in hos_pref.get(h, []):
                invalid_matches += 1

    # Valid matching: no capacity violations and no invalid matches
    valid_matching = cap_violations == 0 and invalid_matches == 0

    # Stable matching: no blocking pairs
    stable_matching = len(blocking_pairs) == 0

    return {
        "valid_matching": valid_matching,
        "stable_matching": stable_matching,
        "capacity_violations": cap_violations,
        "invalid_matches": invalid_matches,
        "blocking_pairs_count": len(blocking_pairs)
    }


def run_correctness_study(dataset_dir: Path):
    groups = group_datasets_by_size(dataset_dir)
    results = []
    
    print("=" * 100)
    print("Correctness Study for Gale-Shapley Algorithm")
    print("=" * 100)
    print(f"Dataset folder: {dataset_dir}")
    print()
    
    print(f"{'Dataset Setting':<25} {'Instances Tested':<15} {'Valid Matchings':<15} {'Stable Matchings':<15} {'Capacity Violations':<20} {'Invalid Matches':<15} {'Avg Blocking Pairs':<18}")
    print("-" * 125)
    
    for (num_h, num_r), files in sorted(groups.items()):
        dataset_results = []
        for file_path in files:
            dataset = load_dataset(file_path)
            result = check_correctness(dataset)
            dataset_results.append(result)
        
        instances_tested = len(dataset_results)
        valid_matchings = sum(1 for r in dataset_results if r["valid_matching"])
        stable_matchings = sum(1 for r in dataset_results if r["stable_matching"])
        total_cap_violations = sum(r["capacity_violations"] for r in dataset_results)
        total_invalid_matches = sum(r["invalid_matches"] for r in dataset_results)
        avg_blocking_pairs = mean(r["blocking_pairs_count"] for r in dataset_results)
        
        setting = f"{num_h} hospitals, {num_r} residents"
        print(f"{setting:<25} {instances_tested:<15} {valid_matchings}/{instances_tested:<14} {stable_matchings}/{instances_tested:<14} {total_cap_violations:<20} {total_invalid_matches:<15} {avg_blocking_pairs:.2f}")
        
        results.append({
            "setting": setting,
            "hospitals": num_h,
            "residents": num_r,
            "instances_tested": instances_tested,
            "valid_matchings": valid_matchings,
            "stable_matchings": stable_matchings,
            "capacity_violations": total_cap_violations,
            "invalid_matches": total_invalid_matches,
            "avg_blocking_pairs": round(avg_blocking_pairs, 2),
        })
    
    return results


def save_correctness_csv(results: list[dict], output_path: Path):
    """Save correctness study results to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "setting",
                "hospitals",
                "residents",
                "instances_tested",
                "valid_matchings",
                "stable_matchings",
                "capacity_violations",
                "invalid_matches",
                "avg_blocking_pairs",
            ],
        )
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(description="Correctness study for Gale-Shapley")
    parser.add_argument(
        "--dataset-dir",
        type=str,
        default=str(DATASET_DIR),
        help="Path to the dataset directory"
    )
    parser.add_argument(
        "--results-dir",
        type=str,
        default=str(RESULTS_DIR),
        help="Path to the results directory"
    )
    
    args = parser.parse_args()
    
    dataset_dir = Path(args.dataset_dir)
    results_dir = Path(args.results_dir)
    
    if not dataset_dir.exists():
        print(f"Dataset directory {dataset_dir} does not exist.")
        return
    
    results = run_correctness_study(dataset_dir)
    
    csv_path = results_dir / "correctness_study.csv"
    save_correctness_csv(results, csv_path)
    print(f"\nCSV saved: {csv_path}")


if __name__ == "__main__":
    main()