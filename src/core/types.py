from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple, Union, Deque, TypedDict, Literal

# ---------- IDs ----------
ResidentId = str
HospitalId = str

# ---------- Lists ----------
HospitalList = List[HospitalId]
ResidentList = List[ResidentId]
BlockingPairs = List[Tuple[ResidentId, HospitalId]]

# ---------- Preferences / capacities ----------
PreferenceList = List[str]
ResidentPreferences = Dict[ResidentId, PreferenceList]
HospitalPreferences = Dict[HospitalId, PreferenceList]
CapacityMap = Dict[HospitalId, int]

# ---------- Matching state ----------
ResidentMatch = Dict[ResidentId, Optional[HospitalId]]
HospitalMatch = Dict[HospitalId, Set[ResidentId]]
HospitalHeld = Dict[HospitalId, List[ResidentId]]  # internal "held list" during algorithm

# ---------- Derived structures ----------
RankTable = Dict[HospitalId, Dict[ResidentId, int]]
EventLog = List[Any]
FreeQueue = Deque[ResidentId]

# ---------- Stable match return shapes ----------
StableMatchResult = Tuple[ResidentMatch, HospitalMatch]
StableMatchResultWithEvents = Tuple[ResidentMatch, HospitalMatch, EventLog]
StableMatchReturn = Union[StableMatchResult, StableMatchResultWithEvents]

# ---------- Auto-mode input shapes ----------
class ResidentInfo(TypedDict, total=False):
    degree: Any
    gpa: Any

class HospitalCriteria(TypedDict, total=False):
    prefDeg: List[Any]

ResidentsInfoMap = Dict[ResidentId, ResidentInfo]
HospitalsCriteriaMap = Dict[HospitalId, HospitalCriteria]

# ---------- Metrics output ----------
MetricName = str
MetricsResult = Dict[MetricName, Any]

# ---------- Explain-unmatched ----------
Mode = Literal["auto", "manual"]

# Cutoff helpers used by explainUnmatched
AutoCutoff = Dict[HospitalId, Optional[Tuple[float, ResidentId]]] # (worstGPA, worstId)
ManualCutoff = Dict[HospitalId, Optional[Tuple[int, ResidentId]]] # (worstRankIndex, worstId)

# The explanation payload is a dict with mixed keys depending on mode.
ExplainPayload = Dict[str, Any]
ExplainUnmatchedResult = List[Tuple[ResidentId, ExplainPayload]]
