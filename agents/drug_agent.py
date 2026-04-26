from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Dict, List

import httpx
from langchain_core.tools import tool


LOCAL_INTERACTION_DB = {
    frozenset({"ibuprofen", "warfarin"}): {
        "risk_level": "high",
        "message": "This combination may increase bleeding risk.",
    },
    frozenset({"metformin", "alcohol"}): {
        "risk_level": "medium",
        "message": "This combination may increase the risk of low blood sugar or acidosis.",
    },
    frozenset({"paracetamol", "alcohol"}): {
        "risk_level": "medium",
        "message": "This combination may increase liver stress.",
    },
}


def _normalize_medications(medications: List[str]) -> List[str]:
    return [item.strip().lower() for item in medications if item.strip()]


@tool
def lookup_local_interaction(medications: List[str]) -> Dict[str, object]:
    """Look up known common medication interactions from a local fallback knowledge base."""
    warnings = []
    for left, right in combinations(_normalize_medications(medications), 2):
        result = LOCAL_INTERACTION_DB.get(frozenset({left, right}))
        if result:
            warnings.append(
                {
                    "drugs": [left, right],
                    "risk_level": result["risk_level"],
                    "source": "local_fallback",
                    "message": result["message"],
                }
            )
    return {"warnings": warnings}


@tool
def lookup_openfda_label(medication: str, base_url: str) -> Dict[str, object]:
    """Fetch warnings and contraindications for a medication from OpenFDA labels."""
    try:
        with httpx.Client(timeout=8.0) as client:
            response = client.get(
                base_url,
                params={"search": f'openfda.generic_name:"{medication}"', "limit": 1},
            )
            response.raise_for_status()
            payload = response.json()
    except Exception as exc:  # noqa: BLE001
        return {
            "medication": medication,
            "source": "openfda_unavailable",
            "warnings": [],
            "contraindications": [],
            "error": str(exc),
        }

    result = payload.get("results", [])
    if not result:
        return {
            "medication": medication,
            "source": "openfda_no_match",
            "warnings": [],
            "contraindications": [],
        }

    first = result[0]
    return {
        "medication": medication,
        "source": "openfda",
        "warnings": first.get("warnings", [])[:2],
        "contraindications": first.get("contraindications", [])[:2],
    }


@dataclass
class DrugInteractionAgent:
    openfda_base_url: str
    tools: List = field(default_factory=lambda: [lookup_local_interaction, lookup_openfda_label])

    def check_interactions(self, medications: List[str]) -> Dict[str, object]:
        meds = _normalize_medications(medications)
        if not meds:
            return {
                "checked_medications": [],
                "warnings": [],
                "overall_risk": "none",
                "summary": "No medications were provided for interaction screening.",
            }

        local_result = lookup_local_interaction.invoke({"medications": meds})
        openfda_results = [
            lookup_openfda_label.invoke({"medication": medication, "base_url": self.openfda_base_url})
            for medication in meds
        ]

        warnings = list(local_result["warnings"])
        for item in openfda_results:
            if item.get("warnings") or item.get("contraindications"):
                warnings.append(
                    {
                        "drugs": [item["medication"]],
                        "risk_level": "medium",
                        "source": item["source"],
                        "message": " ".join(item.get("warnings", []) + item.get("contraindications", []))[:400],
                    }
                )

        overall_risk = "none"
        if any(item["risk_level"] == "high" for item in warnings):
            overall_risk = "high"
        elif any(item["risk_level"] == "medium" for item in warnings):
            overall_risk = "medium"

        summary = (
            "Potential medication warnings found. Please verify with a doctor or pharmacist before use."
            if warnings
            else "No obvious interaction warning was found from the configured sources, but a clinician should still confirm safety."
        )
        return {
            "checked_medications": meds,
            "warnings": warnings,
            "openfda_checks": openfda_results,
            "overall_risk": overall_risk,
            "summary": summary,
        }
