from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from statistics import mean

import matplotlib.pyplot as plt

try:
    from ..generate_dataset import generate_manual_dataset, generate_auto_dataset
    from ..core.gale_shapley import stableMatch, stableMatchWithConst
    from ..dataset_utils import dataset_to_manual_inputs, dataset_to_auto_inputs
except ImportError:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from generate_dataset import generate_manual_dataset, generate_auto_dataset
    from core.gale_shapley import stableMatch, stableMatchWithConst
    from dataset_utils import dataset_to_manual_inputs, dataset_to_auto_inputs


BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR.parent / "dataset"


def save_dataset(dataset: dict, mode: str, hospitals: int, residents: int, trial: int):
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    path = DATASET_DIR / f"{mode}_{hospitals}H_{residents}R_trial{trial}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)
    return path

def run_once(dataset: dict):
    mode = dataset["mode"]

    if mode == "manual":
        res_pref, hos_pref, capacity = dataset_to_manual_inputs(dataset)
        start = time.perf_counter()
        _, _, events = stableMatch(
            res_pref,
            hos_pref,
            capacity,
            returnEvents=True,
            eventMode="json"
        )
        elapsed_ms = (time.perf_counter() - start) * 1000
    else:
        res_pref, res_info, hos_criteria, capacity = dataset_to_auto_inputs(dataset)
        start = time.perf_counter()
        _, _, events = stableMatchWithConst(
            res_pref,
            res_info,
            hos_criteria,
            capacity,
            returnEvents=True,
            eventMode="json"
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

    proposal_count = sum(
        1 for e in events
        if isinstance(e, dict) and e.get("type") == "proposal"
    )

    return elapsed_ms, proposal_count


def make_dataset(mode: str, hospitals: int, residents: int, seed: int | None):
    if mode == "manual":
        return generate_manual_dataset(hospitals, residents, seed)
    return generate_auto_dataset(hospitals, residents, seed)


def build_sizes(start: int, stop: int, step: int):
    return list(range(start, stop + 1, step))


def run_study(mode: str, sizes: list[int], hospital_ratio: float, repeats: int, seed: int | None):
    results = []

    for residents in sizes:
        hospitals = max(1, round(residents * hospital_ratio))
        runtimes = []
        proposals = []

        for trial in range(1, repeats + 1):
            trial_seed = None if seed is None else seed + trial - 1
            dataset = make_dataset(mode, hospitals, residents, trial_seed)
            save_path = save_dataset(dataset, mode, hospitals, residents, trial)

            elapsed_ms, proposal_count = run_once(dataset)
            runtimes.append(elapsed_ms)
            proposals.append(proposal_count)

            print(
                f"  trial {trial}: {elapsed_ms:.4f} ms | "
                f"proposals={proposal_count} | saved={save_path.name}"
            )

        row = {
            "mode": mode,
            "hospitals": hospitals,
            "residents": residents,
            "avg_ms": mean(runtimes),
            "min_ms": min(runtimes),
            "max_ms": max(runtimes),
            "avg_proposals": mean(proposals),
            "min_proposals": min(proposals),
            "max_proposals": max(proposals),
        }
        results.append(row)

        print(
            f"{mode.upper()} | H={hospitals:4d} | R={residents:4d} | "
            f"avg={row['avg_ms']:.4f} ms | proposals={row['avg_proposals']:.2f}"
        )

    return results


def save_csv(results: list[dict], output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "mode",
                "hospitals",
                "residents",
                "avg_ms",
                "min_ms",
                "max_ms",
                "avg_proposals",
                "min_proposals",
                "max_proposals",
            ],
        )
        writer.writeheader()
        writer.writerows(results)


def plot_runtime(results: list[dict], output_path: Path, mode: str):
    x = [row["residents"] for row in results]
    y = [row["avg_ms"] for row in results]

    plt.figure(figsize=(8, 5))
    plt.plot(x, y, marker="o", label="Measured runtime")

    if len(x) >= 2 and y[-1] > 0:
        xn = x[-1]
        yn = y[-1]
        guide = [yn * (xi / xn) ** 2 for xi in x]
        plt.plot(x, guide, linestyle="--", label="O(n²) guide")

    plt.xlabel("Number of Residents")
    plt.ylabel("Average Runtime (ms)")
    plt.title(f"Gale-Shapley Runtime Growth ({mode.capitalize()} mode)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_proposals(results: list[dict], output_path: Path, mode: str):
    x = [row["residents"] for row in results]
    y = [row["avg_proposals"] for row in results]

    plt.figure(figsize=(8, 5))
    plt.plot(x, y, marker="o", label="Average proposals")

    if len(x) >= 2 and y[-1] > 0:
        xn = x[-1]
        yn = y[-1]
        guide = [yn * (xi / xn) ** 2 for xi in x]
        plt.plot(x, guide, linestyle="--", label="O(n²) guide")

    plt.xlabel("Number of Residents")
    plt.ylabel("Average Number of Proposals")
    plt.title(f"Gale-Shapley Proposal Growth ({mode.capitalize()} mode)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Runtime study for Gale-Shapley")
    parser.add_argument("--mode", choices=["manual", "auto"], default="manual")
    parser.add_argument("--start", type=int, default=50)
    parser.add_argument("--stop", type=int, default=500)
    parser.add_argument("--step", type=int, default=50)
    parser.add_argument("--hospital-ratio", type=float, default=0.5)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--csv", type=str, default=str(BASE_DIR.parent / "results" / "runtime_study.csv"))
    parser.add_argument("--runtime-graph", type=str, default=str(BASE_DIR.parent / "results" / "runtime_graph.png"))
    parser.add_argument("--proposal-graph", type=str, default=str(BASE_DIR.parent / "results" / "proposal_graph.png"))
    args = parser.parse_args()

    sizes = build_sizes(args.start, args.stop, args.step)

    print("=" * 68)
    print("Gale-Shapley Runtime Study")
    print("=" * 68)
    print(f"Mode          : {args.mode}")
    print(f"Sizes         : {sizes}")
    print(f"Hospital ratio: {args.hospital_ratio}")
    print(f"Repeats       : {args.repeats}")
    print(f"Seed          : {args.seed}")
    print(f"Dataset folder: {DATASET_DIR}")
    print()

    results = run_study(
        mode=args.mode,
        sizes=sizes,
        hospital_ratio=args.hospital_ratio,
        repeats=args.repeats,
        seed=args.seed,
    )

    save_csv(results, Path(args.csv))
    plot_runtime(results, Path(args.runtime_graph), args.mode)
    plot_proposals(results, Path(args.proposal_graph), args.mode)

    print()
    print(f"CSV saved: {args.csv}")
    print(f"Runtime graph saved: {args.runtime_graph}")
    print(f"Proposal graph saved: {args.proposal_graph}")


if __name__ == "__main__":
    main()