TRIAGE_SAFETY_PROMPT = """
You are Swasthya Sathi's triage safety layer.
Rules:
1. Never diagnose a disease or claim certainty.
2. Only classify urgency: LOW, MEDIUM, HIGH, or EMERGENCY.
3. Always recommend consulting a qualified clinician.
4. If symptoms suggest severe breathing trouble, chest pain, stroke signs, seizures, heavy bleeding,
   pregnancy emergencies, unconsciousness, poisoning, or self-harm risk, classify as EMERGENCY.
5. If details are incomplete, be conservative and advise medical evaluation.
""".strip()


DISCLAIMER = (
    "This assistant does not provide a diagnosis. For any concern, consult a licensed doctor. "
    "If symptoms are severe or worsening, seek urgent medical help immediately."
)


LANGUAGE_STRINGS = {
    "en": {
        "summary_title": "Care guidance",
        "triage_label": "Severity",
        "doctor_fallback": "Please consult a doctor or nearby clinic for a proper evaluation.",
        "emergency": "Go to the nearest emergency service or call local emergency support now.",
        "medication_title": "Medication warnings",
        "route_title": "Nearby care options",
    },
    "hi": {
        "summary_title": "देखभाल मार्गदर्शन",
        "triage_label": "गंभीरता",
        "doctor_fallback": "कृपया सही जांच के लिए डॉक्टर या नजदीकी क्लिनिक से सलाह लें।",
        "emergency": "तुरंत नजदीकी आपातकालीन सेवा पर जाएं या स्थानीय आपातकालीन सहायता लें।",
        "medication_title": "दवा चेतावनी",
        "route_title": "नजदीकी स्वास्थ्य विकल्प",
    },
}
