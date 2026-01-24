from typing import Dict, List, Optional, Set, Tuple

def stableMatch(
    resPref: Dict[str, List[str]],
    hosPref: Dict[str, List[str]],
    capacity: Dict[str, int],
    returnEvents: bool=False,
) -> Tuple[Dict[str, Optional[str]], Dict[str, Set[str]]]:
    
    # Initialize state
    resident = list(resPref.keys())
    hospital = list(hosPref.keys())
    
    nextChoice: Dict[str, int] = {r: 0 for r in resident}
    resMatch: Dict[str, Optional[str]] = {r: None for r in resident}
    hosHeld: Dict[str, List[str]] = {h: [] for h in hospital}
    free: List[str] = [r for r in resident if len(resPref.get(r, [])) > 0]