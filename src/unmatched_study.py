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
RESULTS_DIR = BASE_DIR / "results" / "unmatched"


def analyze_unmatched_rate(dataset: dict) -> float:
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

    mets = metrics(res_pref, hos_pref, capacity, res_match, hos_match, events)
    return mets["Unmatched Rate"] * 100


def run_unmatched_study(dataset_dir: Path) -> list[dict]:
    groups = group_datasets_by_size(dataset_dir)
    results = []

    print("=" * 100)
    print("Unmatched Rate Study for Gale-Shapley")
    print("=" * 100)
    print(f"Dataset folder: {dataset_dir}")
    print()

    for (num_h, num_r), files in sorted(groups.items()):
        rates = []
        for file_path in files:
            dataset = load_dataset(file_path)
            rates.append(analyze_unmatched_rate(dataset))

        avg_rate = mean(rates) if rates else 0.0
        setting = f"{num_h}H, {num_r}R"
        results.append({
            "setting": setting,
            "hospitals": num_h,
            "residents": num_r,
            "instances": len(rates),
            "avg_unmatched_rate": round(avg_rate, 2),
        })

        print(f"{setting:<15} | Avg Unmatched Rate: {avg_rate:6.2f}% | Instances: {len(rates)}")

    return results


def save_unmatched_csv(results: list[dict], output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["setting", "hospitals", "residents", "instances", "avg_unmatched_rate"],
        )
        writer.writeheader()
        writer.writerows(results)


def plot_unmatched_rate(results: list[dict], output_path: Path):
    settings = [r["setting"] for r in results]
    rates = [r["avg_unmatched_rate"] for r in results]

    plt.figure(figsize=(10, 6))
    plt.plot(settings, rates, marker="o", linewidth=2, markersize=8, color="#4c72b0")
    plt.xlabel("Dataset Setting")
    plt.ylabel("Avg Unmatched Rate (%)")
    plt.title("Unmatched Rate by Dataset Setting")
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Unmatched rate study for Gale-Shapley")
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

    results = run_unmatched_study(dataset_dir)
    csv_path = results_dir / "unmatched_study.csv"
    save_unmatched_csv(results, csv_path)
    print(f"CSV saved: {csv_path}")

    plot_unmatched_rate(results, results_dir / "unmatched_graph.png")
    print(f"Graph saved: {results_dir / 'unmatched_graph.png'}")


if __name__ == "__main__":
    main()
