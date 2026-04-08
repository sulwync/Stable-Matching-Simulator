from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path
from statistics import mean

import matplotlib.pyplot as plt

import json

from core.gale_shapley import stableMatch
from dataset_utils import dataset_to_manual_inputs


BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset" / "unluckiest"
RESULTS_DIR = BASE_DIR / "results" / "unluckiest"


def generate_manual_dataset_with_settings(
    num_hospitals: int,
    num_residents: int,
    pref_density: float = 1.0,
    popularity_skew: float = 0.0,
    seed: int | None = None,
) -> dict:
    """Generate a manual dataset with controllable preference density and popularity skew."""
    if seed is not None:
        random.seed(seed)

    hospitals = []
    residents = []

    for _ in range(num_hospitals):
        hospitals.append({"capacity": random.randint(1, 5), "preference": []})

    for _ in range(num_residents):
        residents.append({"preference": []})

    # Preference density defines how many hospitals each resident ranks.
    min_choices = max(1, int(num_hospitals * pref_density * 0.25))
    max_choices = max(1, int(num_hospitals * pref_density))

    # Popularity weights for hospitals.
    if popularity_skew <= 0.0:
        weights = [1.0] * num_hospitals
    else:
        top_share = min(0.9, popularity_skew)
        top_count = max(1, num_hospitals // 5)
        top_weight = top_share / top_count
        other_weight = (1.0 - top_share) / max(1, num_hospitals - top_count)
        weights = [top_weight if i < top_count else other_weight for i in range(num_hospitals)]

    for i in range(num_residents):
        choice_count = random.randint(min_choices, max_choices)
        prefs = random.sample(range(num_hospitals), choice_count)

        if popularity_skew > 0.0:
            prefs.sort(key=lambda h: -weights[h])

        residents[i]["preference"] = [f"H{h+1}" for h in prefs]

    return {"name": "Generated Manual Dataset", "mode": "manual", "hospitals": hospitals, "residents": residents}


def save_unluckiest_dataset(dataset: dict, category: str, trial: int):
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"unluckiest_{category}_trial{trial}.json"
    path = DATASET_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)
    print(f"Saved dataset: {path}")
    return path


def max_proposals_from_events(events: list[str]) -> int:
    counts: dict[str, int] = {}
    for event in events:
        if event.startswith("Proposal:"):
            parts = event.split()
            if len(parts) >= 2:
                r = parts[1]
                counts[r] = counts.get(r, 0) + 1
    return max(counts.values(), default=0)


def run_unluckiest_experiment(datasets: list[dict]) -> dict:
    values = []
    for dataset in datasets:
        res_pref, hos_pref, capacity = dataset_to_manual_inputs(dataset)
        _, _, events = stableMatch(res_pref, hos_pref, capacity, returnEvents=True, eventMode="text")
        values.append(max_proposals_from_events(events))

    return {
        "avg_max_proposals": round(mean(values), 1),
        "datasets": len(values),
        "values": values,
    }


def make_category_datasets(category: str, seed_base: int) -> list[dict]:
    datasets = []

    if category == "balanced":
        params = (50, 50, 0.6, 0.0)
    elif category == "resident_heavy":
        params = (20, 80, 0.6, 0.0)
    elif category == "hospital_heavy":
        params = (80, 20, 0.6, 0.0)
    elif category == "sparse":
        params = (50, 50, 0.2, 0.0)
    elif category == "medium":
        params = (50, 50, 0.5, 0.0)
    elif category == "dense":
        params = (50, 50, 1.0, 0.0)
    elif category == "evenly_distributed":
        params = (50, 50, 0.6, 0.0)
    elif category == "concentrated":
        params = (50, 50, 0.6, 0.7)
    else:
        raise ValueError(f"Unknown category {category}")

    for i in range(3):
        seed = seed_base + i
        num_hospitals, num_residents, pref_density, popularity_skew = params
        data = generate_manual_dataset_with_settings(
            num_hospitals, num_residents, pref_density=pref_density, popularity_skew=popularity_skew, seed=seed
        )
        save_unluckiest_dataset(data, category, i + 1)
        datasets.append(data)

    return datasets


def build_comparison_results() -> list[dict]:
    categories = [
        ("Market Imbalance", ["balanced", "resident_heavy", "hospital_heavy"]),
        ("Preference Density", ["sparse", "medium", "dense"]),
        ("Popularity Concentration", ["evenly_distributed", "concentrated"]),
    ]

    results = []
    for section_name, category_keys in categories:
        section_values = []
        for category_key in category_keys:
            datasets = make_category_datasets(category_key, seed_base=100 if section_name == "Market Imbalance" else 200 if section_name == "Preference Density" else 300)
            summary = run_unluckiest_experiment(datasets)
            category_label = category_key.replace("_", " ").title()
            results.append({
                "section": section_name,
                "category": category_label,
                "avg_max_proposals": summary["avg_max_proposals"],
                "datasets": summary["datasets"],
            })
            section_values.append(summary["avg_max_proposals"])

    return results


def save_unluckiest_csv(results: list[dict], output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["section", "category", "avg_max_proposals", "datasets"],
        )
        writer.writeheader()
        writer.writerows(results)


def plot_section(results: list[dict], section: str, output_path: Path):
    rows = [r for r in results if r["section"] == section and r["category"] != "Section Average"]
    labels = [r["category"] for r in rows]
    values = [r["avg_max_proposals"] for r in rows]

    plt.figure(figsize=(8, 5))
    plt.bar(labels, values, color=["#4c72b0", "#55a868", "#c44e52"][: len(labels)])
    plt.xlabel(section)
    plt.ylabel("Avg Max Proposals")
    plt.title(f"Unluckiest Resident: {section}")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def print_unluckiest_summary(results: list[dict]):
    print("\nUnluckiest Resident Study Results")
    print("=" * 80)
    print(f"{'Section':<25} {'Category':<25} {'Avg Max Proposals':<20} {'Datasets':<10}")
    print("-" * 80)

    for r in results:
        print(f"{r['section']:<25} {r['category']:<25} {r['avg_max_proposals']:<20.1f} {r['datasets']:<10}")


def main():
    parser = argparse.ArgumentParser(description="Unluckiest resident burden study for Gale-Shapley")
    parser.add_argument(
        "--results-dir",
        type=str,
        default=str(RESULTS_DIR),
        help="Path to the results directory"
    )
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    results = build_comparison_results()

    csv_path = results_dir / "unluckiest_study.csv"
    save_unluckiest_csv(results, csv_path)
    print(f"CSV saved: {csv_path}")

    plot_section(results, "Market Imbalance", results_dir / "unluckiest_market_imbalance.png")
    print(f"Graph saved: {results_dir / 'unluckiest_market_imbalance.png'}")

    plot_section(results, "Preference Density", results_dir / "unluckiest_preference_density.png")
    print(f"Graph saved: {results_dir / 'unluckiest_preference_density.png'}")

    plot_section(results, "Popularity Concentration", results_dir / "unluckiest_popularity_concentration.png")
    print(f"Graph saved: {results_dir / 'unluckiest_popularity_concentration.png'}")

    print_unluckiest_summary(results)


if __name__ == "__main__":
    main()
