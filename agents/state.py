from typing import Any, Dict, List, Optional, TypedDict


class AssistantState(TypedDict, total=False):
    symptoms: str
    language: str
    location: str
    medications: List[str]
    transcript: Optional[str]
    triage_result: Dict[str, Any]
    drug_result: Dict[str, Any]
    route_result: Dict[str, Any]
    final_response: Dict[str, Any]
