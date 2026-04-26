from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from agents.prompts import DISCLAIMER, TRIAGE_SAFETY_PROMPT
from rag.retriever import MedicalRAG


SEVERITY_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "EMERGENCY": 3}

EMERGENCY_KEYWORDS = {
    "en": [
        "chest pain",
        "can't breathe",
        "cannot breathe",
        "breathing difficulty",
        "seizure",
        "unconscious",
        "stroke",
        "slurred speech",
        "heavy bleeding",
        "pregnant and bleeding",
        "poison",
        "suicidal",
    ],
    "hi": [
        "सीने में तेज दर्द",
        "सांस नहीं",
        "सांस लेने में बहुत दिक्कत",
        "बेहोश",
        "दौरा",
        "बहुत खून",
        "लकवा",
        "जहर",
    ],
}

HIGH_KEYWORDS = {
    "en": [
        "high fever",
        "fever for 3 days",
        "persistent vomiting",
        "dehydration",
        "blood pressure very high",
        "blood sugar very high",
        "pregnant with pain",
        "rash and fever",
    ],
    "hi": [
        "तेज बुखार",
        "3 दिन से बुखार",
        "बार-बार उल्टी",
        "डिहाइड्रेशन",
        "बहुत ज्यादा दर्द",
    ],
}

MEDIUM_KEYWORDS = {
    "en": [
        "fever",
        "cough",
        "dizziness",
        "diarrhea",
        "rash",
        "mild breathing issue",
        "pain for two days",
    ],
    "hi": [
        "बुखार",
        "खांसी",
        "चक्कर",
        "दस्त",
        "दर्द",
    ],
}

LOW_PATTERNS = {
    "en": [
        "mild cough",
        "runny nose",
        "common cold",
        "no breathing trouble",
        "no chest pain",
    ],
    "hi": [
        "हल्की खांसी",
        "नाक बहना",
        "सांस की दिक्कत नहीं",
    ],
}


@dataclass
class TriageAgent:
    rag: MedicalRAG

    def assess(self, symptoms: str, language: str = "en") -> Dict[str, object]:
        normalized = symptoms.lower().strip()
        severity = self._rule_based_severity(normalized, language)
        evidence = self.rag.retrieve_guidance(symptoms, top_k=3)

        advice_lines = [
            TRIAGE_SAFETY_PROMPT,
            "Relevant public-health guidance:",
            *[f"- {item['content']}" for item in evidence],
        ]

        action_items = self._action_items(severity, language)
        return {
            "severity": severity,
            "action_items": action_items,
            "retrieved_guidance": evidence,
            "safety_prompt": TRIAGE_SAFETY_PROMPT,
            "advice_summary": " ".join(action_items) + " " + DISCLAIMER,
            "raw_context": "\n".join(advice_lines),
        }

    def _rule_based_severity(self, symptoms: str, language: str) -> str:
        low_patterns = LOW_PATTERNS.get(language, []) + LOW_PATTERNS["en"]
        if any(pattern in symptoms for pattern in low_patterns):
            return "LOW"

        matched = "LOW"
        for level, keywords in [
            ("EMERGENCY", EMERGENCY_KEYWORDS.get(language, []) + EMERGENCY_KEYWORDS["en"]),
            ("HIGH", HIGH_KEYWORDS.get(language, []) + HIGH_KEYWORDS["en"]),
            ("MEDIUM", MEDIUM_KEYWORDS.get(language, []) + MEDIUM_KEYWORDS["en"]),
        ]:
            if any(keyword in symptoms for keyword in keywords):
                matched = level
                break

        if len(symptoms.split()) < 3 and matched == "LOW":
            return "MEDIUM"
        return matched

    def _action_items(self, severity: str, language: str) -> List[str]:
        english = {
            "LOW": [
                "Monitor symptoms, stay hydrated, and rest.",
                "If symptoms worsen or last beyond 24-48 hours, see a clinician.",
            ],
            "MEDIUM": [
                "Arrange a doctor or clinic visit within 24 hours.",
                "Watch for worsening fever, breathing issues, dehydration, or confusion.",
            ],
            "HIGH": [
                "Seek urgent medical evaluation as soon as possible today.",
                "Avoid self-medicating beyond basic supportive care unless a clinician advised it.",
            ],
            "EMERGENCY": [
                "This needs emergency care right now.",
                "Go to the nearest emergency facility or contact local emergency support immediately.",
            ],
        }
        hindi = {
            "LOW": [
                "लक्षणों पर नजर रखें, आराम करें और पानी पीते रहें।",
                "अगर 24-48 घंटे में सुधार न हो या हालत बिगड़े तो डॉक्टर से मिलें।",
            ],
            "MEDIUM": [
                "24 घंटे के भीतर डॉक्टर या क्लिनिक में जांच कराएं।",
                "अगर बुखार, सांस की दिक्कत, कमजोरी या उलझन बढ़े तो तुरंत मदद लें।",
            ],
            "HIGH": [
                "आज ही जल्दी से जल्दी डॉक्टर द्वारा जांच कराएं।",
                "डॉक्टर की सलाह के बिना अतिरिक्त दवा न लें।",
            ],
            "EMERGENCY": [
                "यह आपातकालीन स्थिति हो सकती है।",
                "तुरंत नजदीकी आपातकालीन केंद्र जाएं या स्थानीय आपात सहायता लें।",
            ],
        }
        table = hindi if language == "hi" else english
        return table[severity]
