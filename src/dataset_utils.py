import json
from pathlib import Path
from typing import Dict, List, Tuple, Any

from core.types import (
    ResidentId, HospitalId, ResidentPreferences, HospitalPreferences, CapacityMap,
    ResidentMatch, HospitalMatch, ResidentsInfoMap, HospitalsCriteriaMap
)


def dataset_to_manual_inputs(dataset: dict) -> Tuple[ResidentPreferences, HospitalPreferences, CapacityMap]:
    hospitals = dataset["hospitals"]
    residents = dataset["residents"]

    res_pref = {
        f"R{i+1}": resident.get("preference", [])
        for i, resident in enumerate(residents)
    }

    hos_pref = {
        f"H{i+1}": hospital.get("preference", [])
        for i, hospital in enumerate(hospitals)
    }

    capacity = {
        f"H{i+1}": hospital.get("capacity", 0)
        for i, hospital in enumerate(hospitals)
    }

    return res_pref, hos_pref, capacity


def dataset_to_auto_inputs(dataset: dict) -> Tuple[ResidentPreferences, ResidentsInfoMap, HospitalsCriteriaMap, CapacityMap]:
    hospitals = dataset["hospitals"]
    residents = dataset["residents"]

    res_pref = {
        f"R{i+1}": resident.get("preference", [])
        for i, resident in enumerate(residents)
    }

    res_info = {
        f"R{i+1}": {
            "gpa": resident.get("gpa", 0.0),
            "degree": resident.get("degree", "")
        }
        for i, resident in enumerate(residents)
    }

    hos_criteria = {
        f"H{i+1}": {
            "prefDeg": [hospital.get("pref_degree", "All")]
        }
        for i, hospital in enumerate(hospitals)
    }

    capacity = {
        f"H{i+1}": hospital.get("capacity", 0)
        for i, hospital in enumerate(hospitals)
    }

    return res_pref, res_info, hos_criteria, capacity


def load_dataset(file_path: Path) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_dataset_filename(filename: str) -> Tuple[str, int, int, int]:
    # e.g., manual_25H_50R_trial1.json -> mode, 25, 50, 1
    parts = filename.replace(".json", "").split("_")
    mode = parts[0]
    h_part = parts[1]  # 25H
    r_part = parts[2]  # 50R
    trial_part = parts[3]  # trial1
    num_h = int(h_part[:-1])
    num_r = int(r_part[:-1])
    trial = int(trial_part[5:])
    return mode, num_h, num_r, trial


def group_datasets_by_size(dataset_dir: Path) -> Dict[Tuple[int, int], List[Path]]:
    groups = {}
    for file_path in dataset_dir.glob("*.json"):
        try:
            mode, num_h, num_r, trial = parse_dataset_filename(file_path.name)
            key = (num_h, num_r)
            if key not in groups:
                groups[key] = []
            groups[key].append(file_path)
        except ValueError:
            continue  # skip invalid filenames
    return groups