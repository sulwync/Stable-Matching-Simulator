from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

from core.gale_shapley import stableMatch, stableMatchWithConst, generateHosPref
from core.metrics import metrics
from core.explain_unmatched import explainUnmatched


def parse_tokens(s: str) -> List[str]:
    if not s:
        return []
    return [t.strip() for t in s.replace(",", " ").split() if t.strip()]


def to_int(s: str) -> Optional[int]:
    try:
        return int(s)
    except Exception:
        return None


def to_float(s: str) -> Optional[float]:
    try:
        return float(s)
    except Exception:
        return None


@dataclass
class RunResult:
    mode: str
    resMatch: Dict[str, Optional[str]]
    hosMatch: Dict[str, Set[str]]
    stats: Dict[str, Any]
    unmatched_explain: Any
    hosPref: Optional[Dict[str, List[str]]] = None
    events: Optional[List[str]] = None
    events_json: Optional[List[Dict[str, Any]]] = None


class AppController:
    def run(
        self,
        *,
        is_auto: bool,
        hospitals: List[Dict[str, Any]],
        residents: List[Dict[str, Any]],
    ) -> RunResult:

        # IDs
        H: List[str] = [f"H{i+1}" for i in range(len(hospitals))]
        R: List[str] = [f"R{i+1}" for i in range(len(residents))]
        Hset = set(H)
        Rset = set(R)

        # Capacity
        capacity: Dict[str, int] = {}
        for hid, row in zip(H, hospitals):
            cap_s = (row.get("capacity_str") or "").strip()
            cap_v = to_int(cap_s)
            capacity[hid] = cap_v if (cap_v is not None and cap_v > 0) else 0

        # Resident Preferences
        resPref: Dict[str, List[str]] = {}
        for rid, row in zip(R, residents):
            raw = (row.get("pref_str") or "").strip()
            prefs = [h for h in parse_tokens(raw) if h in Hset]
            resPref[rid] = prefs

        # Manual mode
        if not is_auto:
            hosPref: Dict[str, List[str]] = {}
            for hid, row in zip(H, hospitals):
                raw = (row.get("manual_pref_str") or "").strip()
                prefs = [r for r in parse_tokens(raw) if r in Rset]
                hosPref[hid] = prefs

            # Text events for OutputView
            resMatch, hosMatch, events = stableMatch(
                resPref, hosPref, capacity,
                returnEvents=True
            )

            # JSON events for D3
            _, _, events_json = stableMatch(
                resPref, hosPref, capacity,
                returnEvents=True,
                eventMode="json"
            )

            stats = metrics(resPref, hosPref, capacity, resMatch, hosMatch, events=events)

            unmatched_explain = explainUnmatched(
                "manual",
                resPref=resPref,
                resMatch=resMatch,
                hosMatch=hosMatch,
                hosPref=hosPref,
            )

            return RunResult(
                mode="manual",
                resMatch=resMatch,
                hosMatch=hosMatch,
                stats=stats,
                unmatched_explain=unmatched_explain,
                hosPref=hosPref,
                events=events,
                events_json=events_json,
            )

        # Auto mode
        resInfo: Dict[str, Dict[str, Any]] = {}
        for rid, row in zip(R, residents):
            gpa_s = (row.get("gpa_str") or "").strip()
            deg_s = (row.get("deg_str") or "").strip()
            gpa_v = to_float(gpa_s)

            resInfo[rid] = {
                "gpa": gpa_v if gpa_v is not None else 0.0,
                "degree": deg_s if deg_s else None,
            }

        hosCriteria: Dict[str, Dict[str, Any]] = {}
        for hid, row in zip(H, hospitals):
            pref_deg = (row.get("pref_deg_str") or "").strip()
            hosCriteria[hid] = {"prefDeg": [pref_deg] if pref_deg else []}

        # Displayable generated hospital preference
        hosPref = generateHosPref(resInfo, hosCriteria)

        # Text events
        resMatch, hosMatch, events = stableMatchWithConst(
            resPref, resInfo, hosCriteria, capacity,
            returnEvents=True
        )

        # JSON events
        _, _, events_json = stableMatchWithConst(
            resPref, resInfo, hosCriteria, capacity,
            returnEvents=True,
            eventMode="json"
        )

        stats = metrics(resPref, hosPref, capacity, resMatch, hosMatch, events=events)

        unmatched_explain = explainUnmatched(
            "auto",
            resPref=resPref,
            resMatch=resMatch,
            hosMatch=hosMatch,
            resInfo=resInfo,
            hosCriteria=hosCriteria,
        )

        return RunResult(
            mode="auto",
            resMatch=resMatch,
            hosMatch=hosMatch,
            stats=stats,
            unmatched_explain=unmatched_explain,
            hosPref=hosPref,
            events=events,
            events_json=events_json,
        )