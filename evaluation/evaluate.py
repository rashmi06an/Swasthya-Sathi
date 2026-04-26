"""
Swasthya Sathi Evaluation Script
=================================
Runs all sample test cases against the live agents pipeline
and reports accuracy + response quality metrics.

Usage:
    python -m evaluation.evaluate              # runs all 15 test cases
    python -m evaluation.evaluate --case TC001 # single case
    python -m evaluation.evaluate --json       # JSON output
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure project root is on sys.path when run as a module
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from agents.drug_agent import DrugInteractionAgent
from agents.orchestrator import SwasthyaSathiGraph
from agents.routing_agent import RoutingAgent
from agents.triage_agent import TriageAgent
from api.config import get_settings
from rag.retriever import MedicalRAG

_GUIDELINES = _ROOT / "data" / "who_guidelines.md"
_FACILITIES = _ROOT / "data" / "healthcare_facilities.csv"
_CASES = _ROOT / "data" / "sample_cases.json"

SEVERITY_LEVELS = ["LOW", "MEDIUM", "HIGH", "EMERGENCY"]
SEVERITY_COLOR_MAP = {
    "LOW": "green",
    "MEDIUM": "yellow",
    "HIGH": "orange",
    "EMERGENCY": "red",
}


@dataclass
class CaseResult:
    case_id: str
    description: str
    passed: bool
    latency_ms: float
    severity_predicted: str
    severity_expected: Optional[str]
    severity_correct: bool
    color_correct: bool
    drug_risk_correct: bool
    has_facilities: bool
    has_disclaimer: bool
    failures: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "description": self.description,
            "passed": self.passed,
            "latency_ms": round(self.latency_ms, 1),
            "severity_predicted": self.severity_predicted,
            "severity_expected": self.severity_expected,
            "severity_correct": self.severity_correct,
            "color_correct": self.color_correct,
            "drug_risk_correct": self.drug_risk_correct,
            "has_facilities": self.has_facilities,
            "has_disclaimer": self.has_disclaimer,
            "failures": self.failures,
        }


def _build_graph() -> SwasthyaSathiGraph:
    settings = get_settings()
    rag = MedicalRAG(guideline_path=str(_GUIDELINES), embedding_model=settings.embedding_model)
    triage = TriageAgent(rag=rag)
    drug = DrugInteractionAgent(openfda_base_url=settings.openfda_base_url)
    routing = RoutingAgent(facility_csv_path=str(_FACILITIES))
    return SwasthyaSathiGraph(triage_agent=triage, drug_agent=drug, routing_agent=routing)


def _run_case(graph: SwasthyaSathiGraph, case: Dict[str, Any]) -> CaseResult:
    inp = case["input"]
    expected = case.get("expected", {})
    failures: List[str] = []

    t0 = time.perf_counter()
    try:
        result = graph.invoke(
            symptoms=inp["symptoms"],
            language=inp["language"],
            location=inp["location"],
            medications=inp.get("medications", []),
        )
    except Exception as exc:  # noqa: BLE001
        return CaseResult(
            case_id=case["id"],
            description=case["description"],
            passed=False,
            latency_ms=0.0,
            severity_predicted="ERROR",
            severity_expected=expected.get("severity"),
            severity_correct=False,
            color_correct=False,
            drug_risk_correct=False,
            has_facilities=False,
            has_disclaimer=False,
            failures=[f"Exception: {exc}"],
        )
    latency_ms = (time.perf_counter() - t0) * 1000

    predicted_severity = result.get("severity", "UNKNOWN")
    predicted_color = result.get("severity_color", "")

    # Severity accuracy
    exp_severity = expected.get("severity")
    severity_correct = (exp_severity is None) or (predicted_severity == exp_severity)
    if not severity_correct:
        failures.append(f"severity: expected={exp_severity}, got={predicted_severity}")

    # Color accuracy
    exp_color = SEVERITY_COLOR_MAP.get(predicted_severity, "")
    color_correct = (predicted_color == exp_color)
    if not color_correct:
        failures.append(f"color: expected={exp_color}, got={predicted_color}")

    # Drug risk check
    exp_drug_risk = expected.get("drug_overall_risk")
    drug_result = result.get("drug", {})
    actual_drug_risk = drug_result.get("overall_risk", "none")
    drug_risk_correct = (exp_drug_risk is None) or (actual_drug_risk == exp_drug_risk)
    if not drug_risk_correct:
        failures.append(f"drug_risk: expected={exp_drug_risk}, got={actual_drug_risk}")

    # Has facilities
    routing_result = result.get("routing", {})
    facilities = routing_result.get("facilities", [])
    has_facilities = len(facilities) > 0
    if expected.get("has_facilities") and not has_facilities:
        failures.append("routing: no facilities returned")

    # Disclaimer presence
    message = result.get("message", "")
    disclaimer = result.get("disclaimer", "")
    has_disclaimer = "consult" in message.lower() or "consult" in disclaimer.lower()
    if not has_disclaimer:
        failures.append("safety: disclaimer/consult message missing from response")

    return CaseResult(
        case_id=case["id"],
        description=case["description"],
        passed=len(failures) == 0,
        latency_ms=latency_ms,
        severity_predicted=predicted_severity,
        severity_expected=exp_severity,
        severity_correct=severity_correct,
        color_correct=color_correct,
        drug_risk_correct=drug_risk_correct,
        has_facilities=has_facilities,
        has_disclaimer=has_disclaimer,
        failures=failures,
    )


def _print_results(results: List[CaseResult], json_output: bool = False) -> None:
    if json_output:
        summary = {
            "total": len(results),
            "passed": sum(r.passed for r in results),
            "failed": sum(not r.passed for r in results),
            "severity_accuracy": round(
                sum(r.severity_correct for r in results) / len(results) * 100, 1
            ),
            "avg_latency_ms": round(
                sum(r.latency_ms for r in results) / len(results), 1
            ),
            "cases": [r.to_dict() for r in results],
        }
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return

    sep = "─" * 72
    print(f"\n{'Swasthya Sathi — Evaluation Report':^72}")
    print(sep)
    print(f"{'ID':<8} {'PASS':<6} {'PREDICTED':<12} {'EXPECTED':<12} {'LAT(ms)':<10} FAILURES")
    print(sep)
    for r in results:
        status = "✅ PASS" if r.passed else "❌ FAIL"
        exp = r.severity_expected or "—"
        failures_str = "; ".join(r.failures) if r.failures else "—"
        print(f"{r.case_id:<8} {status:<6} {r.severity_predicted:<12} {exp:<12} {r.latency_ms:<10.1f} {failures_str}")

    print(sep)
    total = len(results)
    passed = sum(r.passed for r in results)
    severity_acc = sum(r.severity_correct for r in results) / total * 100
    drug_acc = sum(r.drug_risk_correct for r in results) / total * 100
    disclaimer_rate = sum(r.has_disclaimer for r in results) / total * 100
    avg_lat = sum(r.latency_ms for r in results) / total

    print(f"\n{'SUMMARY':^72}")
    print(f"  Total cases      : {total}")
    print(f"  Passed           : {passed}  ({passed/total*100:.1f}%)")
    print(f"  Failed           : {total-passed}")
    print(f"  Severity Accuracy: {severity_acc:.1f}%")
    print(f"  Drug Risk Accuracy: {drug_acc:.1f}%")
    print(f"  Disclaimer Rate  : {disclaimer_rate:.1f}%")
    print(f"  Avg Latency      : {avg_lat:.1f} ms")
    print(sep)

    if passed == total:
        print("  🎉 All tests passed!")
    else:
        print(f"  ⚠️  {total - passed} test(s) failed. Review failures above.")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Swasthya Sathi agents")
    parser.add_argument("--case", help="Run only this case ID (e.g. TC001)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    cases: List[Dict[str, Any]] = json.loads(_CASES.read_text(encoding="utf-8"))
    if args.case:
        cases = [c for c in cases if c["id"] == args.case]
        if not cases:
            print(f"No case found with ID={args.case}")
            sys.exit(1)

    print(f"Loading agents (embedding model will download on first run)…")
    graph = _build_graph()
    print(f"Running {len(cases)} test case(s)…\n")

    results = []
    for case in cases:
        if not args.json:
            print(f"  Running {case['id']}: {case['description']}…", end=" ", flush=True)
        result = _run_case(graph, case)
        results.append(result)
        if not args.json:
            print("PASS" if result.passed else f"FAIL ({'; '.join(result.failures)})")

    _print_results(results, json_output=args.json)
    sys.exit(0 if all(r.passed for r in results) else 1)


if __name__ == "__main__":
    main()
