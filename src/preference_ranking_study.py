from __future__ import annotations

import argparse
import csv
from pathlib import Path
from statistics import mean

import matplotlib.pyplot as plt

from core.gale_shapley import stableMatch, generateHosPref
from core.metrics import metrics
from dataset_utils import load_dataset, group_datasets_by_size, dataset_to_manual_inputs, dataset_to_auto_inputs


BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset" / "runtime"
RESULTS_DIR = BASE_DIR / "results" / "preference_ranking"


def analyze_preference_ranks(dataset: dict) -> tuple[float, float]:
    mode = dataset["mode"]
    if mode == "manual":
        res_pref, hos_pref, capacity = dataset_to_manual_inputs(dataset)
        res_match, hos_match, events = stableMatch(
            res_pref, hos_pref, capacity, returnEvents=True, eventMode="text"
        )
    else:
        res_pref, res_info, hos_criteria, capacity = dataset_to_auto_inputs(dataset)
        hos_pref = generateHosPref(res_info, hos_criteria)
        res_match, hos_match, events = stableMatch(
            res_pref, hos_pref, capacity, returnEvents=True, eventMode="text"
        )

    # Compute normalized ranks
    res_normalized = []
    for r, h in res_match.items():
        if h is not None:
            prefs = res_pref.get(r, [])
            if h in prefs and len(prefs) > 1:
                rank = prefs.index(h) + 1
                normalized = (rank - 1) / (len(prefs) - 1)
                res_normalized.append(normalized)

    avg_res_normalized = mean(res_normalized) * 100 if res_normalized else 0.0

    hos_normalized = []
    for h, rs in hos_match.items():
        prefs = hos_pref.get(h, [])
        if len(prefs) > 1:
            for r in rs:
                if r in prefs:
                    rank = prefs.index(r) + 1
                    normalized = (rank - 1) / (len(prefs) - 1)
                    hos_normalized.append(normalized)

    avg_hos_normalized = mean(hos_normalized) * 100 if hos_normalized else 0.0

    return avg_res_normalized, avg_hos_normalized


def run_preference_ranking_study(dataset_dir: Path) -> list[dict]:
    groups = group_datasets_by_size(dataset_dir)
    results = []

    print("=" * 100)
    print("Preference Ranking Study for Gale-Shapley")
    print("=" * 100)
    print(f"Dataset folder: {dataset_dir}")
    print()

    for (num_h, num_r), files in sorted(groups.items()):
        resident_ranks = []
        hospital_ranks = []
        for file_path in files:
            dataset = load_dataset(file_path)
            resident_rank, hospital_rank = analyze_preference_ranks(dataset)
            resident_ranks.append(resident_rank)
            hospital_ranks.append(hospital_rank)

        avg_res_rank = mean(resident_ranks) if resident_ranks else 0.0
        avg_hos_rank = mean(hospital_ranks) if hospital_ranks else 0.0
        setting = f"{num_h}H, {num_r}R"
        results.append({
            "setting": setting,
            "hospitals": num_h,
            "residents": num_r,
            "instances": len(files),
            "avg_resident_rank_pct": round(avg_res_rank, 2),
            "avg_hospital_rank_pct": round(avg_hos_rank, 2),
        })

        print(
            f"{setting:<15} | Resident Rank: {avg_res_rank:5.2f}% | "
            f"Hospital Rank: {avg_hos_rank:5.2f}% | Instances: {len(files)}"
        )

    return results


def save_preference_csv(results: list[dict], output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["setting", "hospitals", "residents", "instances", "avg_resident_rank_pct", "avg_hospital_rank_pct"],
        )
        writer.writeheader()
        writer.writerows(results)


def plot_preference_ranks(results: list[dict], output_path: Path):
    settings = [r["setting"] for r in results]
    resident_ranks = [r["avg_resident_rank_pct"] for r in results]
    hospital_ranks = [r["avg_hospital_rank_pct"] for r in results]

    plt.figure(figsize=(10, 6))
    x = range(len(settings))
    plt.plot(x, resident_ranks, marker="o", label="Resident Rank (%)", linewidth=2, markersize=8)
    plt.plot(x, hospital_ranks, marker="s", label="Hospital Rank (%)", linewidth=2, markersize=8)
    plt.xticks(x, settings, rotation=45, ha="right")
    plt.xlabel("Dataset Setting")
    plt.ylabel("Average Preference Rank (0% = top choice, 100% = worst choice)")
    plt.title("Normalized Preference Rank Comparison")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Preference ranking study for Gale-Shapley")
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

    results = run_preference_ranking_study(dataset_dir)
    csv_path = results_dir / "preference_ranking_study.csv"
    save_preference_csv(results, csv_path)
    print(f"CSV saved: {csv_path}")

    plot_preference_ranks(results, results_dir / "preference_ranking_graph.png")
    print(f"Graph saved: {results_dir / 'preference_ranking_graph.png'}")


if __name__ == "__main__":
    main()
