from __future__ import annotations

from dataclasses import dataclass

from langgraph.graph import END, START, StateGraph

from agents.drug_agent import DrugInteractionAgent
from agents.prompts import DISCLAIMER, LANGUAGE_STRINGS
from agents.routing_agent import RoutingAgent
from agents.state import AssistantState
from agents.triage_agent import TriageAgent


@dataclass
class SwasthyaSathiGraph:
    triage_agent: TriageAgent
    drug_agent: DrugInteractionAgent
    routing_agent: RoutingAgent

    def __post_init__(self) -> None:
        graph = StateGraph(AssistantState)
        graph.add_node("triage", self._triage_node)
        graph.add_node("drug", self._drug_node)
        graph.add_node("routing", self._routing_node)
        graph.add_node("finalize", self._finalize_node)

        graph.add_edge(START, "triage")
        graph.add_edge("triage", "drug")
        graph.add_edge("drug", "routing")
        graph.add_edge("routing", "finalize")
        graph.add_edge("finalize", END)
        self.graph = graph.compile()

    def invoke(self, symptoms: str, language: str, location: str, medications: list[str]) -> dict:
        initial_state: AssistantState = {
            "symptoms": symptoms,
            "language": language,
            "location": location,
            "medications": medications,
        }
        result = self.graph.invoke(initial_state)
        return result["final_response"]

    def _triage_node(self, state: AssistantState) -> AssistantState:
        return {
            "triage_result": self.triage_agent.assess(
                symptoms=state["symptoms"],
                language=state.get("language", "en"),
            )
        }

    def _drug_node(self, state: AssistantState) -> AssistantState:
        return {"drug_result": self.drug_agent.check_interactions(state.get("medications", []))}

    def _routing_node(self, state: AssistantState) -> AssistantState:
        return {"route_result": self.routing_agent.find_nearest(state.get("location", "sehore"))}

    def _finalize_node(self, state: AssistantState) -> AssistantState:
        language = state.get("language", "en")
        strings = LANGUAGE_STRINGS.get(language, LANGUAGE_STRINGS["en"])
        triage = state["triage_result"]
        drug = state["drug_result"]
        route = state["route_result"]

        medication_lines = [
            warning["message"] for warning in drug["warnings"][:3] if warning.get("message")
        ] or [drug["summary"]]

        route_lines = [
            f"{item['name']} ({item['type']}) - {item['distance_km']} km - {item['phone']}"
            for item in route["facilities"]
        ]

        summary = {
            "severity": triage["severity"],
            "severity_color": {
                "LOW": "green",
                "MEDIUM": "yellow",
                "HIGH": "orange",
                "EMERGENCY": "red",
            }[triage["severity"]],
            "message": (
                f"{strings['triage_label']}: {triage['severity']}\n\n"
                + "\n".join(triage["action_items"])
                + "\n\n"
                + f"{strings['medication_title']}: "
                + " | ".join(medication_lines)
                + "\n\n"
                + f"{strings['route_title']}:\n"
                + "\n".join(route_lines)
                + "\n\n"
                + DISCLAIMER
            ),
            "disclaimer": DISCLAIMER,
            "triage": triage,
            "drug": drug,
            "routing": route,
        }
        return {"final_response": summary}
