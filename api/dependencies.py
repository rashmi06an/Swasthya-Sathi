"""FastAPI dependency injection for Swasthya Sathi."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from agents.drug_agent import DrugInteractionAgent
from agents.orchestrator import SwasthyaSathiGraph
from agents.routing_agent import RoutingAgent
from agents.triage_agent import TriageAgent
from api.config import get_settings
from rag.retriever import MedicalRAG

# Resolve data paths relative to project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_GUIDELINES_PATH = _PROJECT_ROOT / "data" / "who_guidelines.md"
_FACILITIES_PATH = _PROJECT_ROOT / "data" / "healthcare_facilities.csv"


@lru_cache(maxsize=1)
def get_graph() -> SwasthyaSathiGraph:
    """Build and cache the LangGraph orchestrator with all agents.

    This is cached so the expensive model loading (embeddings, Whisper)
    only happens once per process.
    """
    settings = get_settings()

    rag = MedicalRAG(
        guideline_path=str(_GUIDELINES_PATH),
        embedding_model=settings.embedding_model,
    )

    triage = TriageAgent(rag=rag)
    drug = DrugInteractionAgent(openfda_base_url=settings.openfda_base_url)
    routing = RoutingAgent(facility_csv_path=str(_FACILITIES_PATH))

    return SwasthyaSathiGraph(
        triage_agent=triage,
        drug_agent=drug,
        routing_agent=routing,
    )
