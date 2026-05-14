"""
Swasthya Sathi — Streamlit Frontend
Voice-first rural health assistant.
"""
from __future__ import annotations

import os
from io import BytesIO

import httpx
import streamlit as st

# ─── Config ──────────────────────────────────────────────────────────────────
def _get_backend_url() -> str:
    """Read BACKEND_URL from secrets (HF Spaces) or env var, with safe fallback."""
    # 1. Try streamlit secrets (for HF Spaces, Streamlit Cloud)
    try:
        url = st.secrets.get("BACKEND_URL", None)
        if url:
            return url.strip().rstrip("/")
    except Exception:
        pass

    # 2. Try environment variable
    env_url = os.environ.get("BACKEND_URL", "").strip().rstrip("/")
    if env_url:
        return env_url

    # 3. Default to localhost for single-container or local dev
    return "http://localhost:8000"

BACKEND_URL = _get_backend_url()

DISCLAIMER = (
    "⚠️ Swasthya Sathi is a triage support tool only. It does **not** diagnose "
    "disease and does **not** replace a qualified doctor. Always consult a licensed "
    "healthcare professional. If symptoms are severe or life-threatening, "
    "seek emergency care immediately. **Dial 108** for ambulance."
)

LOCATION_OPTIONS = ["Sehore", "Bhopal", "Indore"]

SEVERITY_PALETTE = {
    "green":  {"bg": "#d1fae5", "border": "#10b981", "text": "#065f46"},
    "yellow": {"bg": "#fef9c3", "border": "#f59e0b", "text": "#78350f"},
    "orange": {"bg": "#ffedd5", "border": "#f97316", "text": "#7c2d12"},
    "red":    {"bg": "#fee2e2", "border": "#ef4444", "text": "#7f1d1d"},
}

# ─── Translations ─────────────────────────────────────────────────────────────
TRANSLATIONS = {
    "en": {
        "title": "🩺 Swasthya Sathi",
        "subtitle": "Agentic rural health assistant — safe triage · drug interaction check · nearest care routing",
        "desc_symptoms": "#### 📝 Describe Symptoms",
        "lang_label": "Language / भाषा",
        "loc_label": "Nearest Location",
        "med_label": "Current medicines (comma-separated)",
        "med_placeholder": "e.g. paracetamol, metformin",
        "symp_placeholder": "Example: High fever for 3 days, dizziness and body ache\nउदाहरण: 3 दिन से तेज बुखार, चक्कर और बदन दर्द",
        "symp_label": "Symptoms",
        "analyse_btn": "🔍 Analyse Symptoms",
        "voice_input": "#### 🎤 Voice Input",
        "voice_placeholder": "Speak your symptoms",
        "voice_caption": "Speak in English or Hindi. Audio is transcribed using Whisper and a voice response is generated using gTTS.",
        "emergency_title": "#### ℹ️ Emergency Numbers",
        "ambulance": "🚑 **108** — Ambulance (national)",
        "women": "👩 **181** — Women's helpline",
        "child": "👶 **1098** — Child helpline",
        "mental": "🧠 **iCall: 9152987821** — Mental health",
        "assessment_title": "### 📋 Assessment Result",
        "severity_label": "Severity",
        "guidance_label": "Guidance",
        "drug_warn_label": "Drug Interaction Warnings",
        "overall_risk": "Overall risk",
        "no_drug_warn": "✅ No drug interaction warnings found for provided medications.",
        "nearest_health_label": "Nearest Healthcare",
        "voice_res_label": "Voice Response",
        "session_history": "### 📜 Session History",
        "running_triage": "Running triage agents…",
        "transcribing": "Transcribing audio and running triage agents…",
        "generating_voice": "Generating audio response…",
    },
    "hi": {
        "title": "🩺 स्वास्थ्य साथी",
        "subtitle": "एजेंटिक ग्रामीण स्वास्थ्य सहायक — सुरक्षित ट्राइएज · दवा इंटरेक्शन जांच · निकटतम देखभाल रूटिंग",
        "desc_symptoms": "#### 📝 लक्षणों का वर्णन करें",
        "lang_label": "भाषा / Language",
        "loc_label": "निकटतम स्थान",
        "med_label": "वर्तमान दवाएं (अल्पविराम से अलग)",
        "med_placeholder": "जैसे: पैरासिटामोल, मेटफोर्मिन",
        "symp_placeholder": "उदाहरण: 3 दिन से तेज बुखार, चक्कर और बदन दर्द",
        "symp_label": "लक्षण",
        "analyse_btn": "🔍 लक्षणों का विश्लेषण करें",
        "voice_input": "#### 🎤 वॉयस इनपुट",
        "voice_placeholder": "अपने लक्षण बोलें",
        "voice_caption": "अंग्रेजी या हिंदी में बोलें। व्हिस्पर का उपयोग करके ऑडियो ट्रांसक्राइब किया जाता है और gTTS का उपयोग करके वॉयस रिस्पॉन्स जनरेट किया जाता है।",
        "emergency_title": "#### ℹ️ आपातकालीन नंबर",
        "ambulance": "🚑 **108** — एम्बुलेंस (राष्ट्रीय)",
        "women": "👩 **181** — महिला हेल्पलाइन",
        "child": "👶 **1098** — चाइल्ड हेल्पलाइन",
        "mental": "🧠 **iCall: 9152987821** — मानसिक स्वास्थ्य",
        "assessment_title": "### 📋 मूल्यांकन परिणाम",
        "severity_label": "गंभीरता",
        "guidance_label": "मार्गदर्शन",
        "drug_warn_label": "दवा इंटरेक्शन चेतावनी",
        "overall_risk": "कुल जोखिम",
        "no_drug_warn": "✅ प्रदान की गई दवाओं के लिए कोई दवा इंटरेक्शन चेतावनी नहीं मिली।",
        "nearest_health_label": "निकटतम स्वास्थ्य सेवा",
        "voice_res_label": "वॉयस रिस्पॉन्स",
        "session_history": "### 📜 सत्र इतिहास",
        "running_triage": "ट्राइएज एजेंट चल रहे हैं…",
        "transcribing": "ऑडियो ट्रांसक्राइब करना और ट्राइएज एजेंट चलाना…",
        "generating_voice": "ऑडियो रिस्पॉन्स जनरेट हो रहा है…",
    }
}

import json
def _get_locations() -> list[str]:
    try:
        with open("data/indian_districts.json", "r") as f:
            return json.load(f)
    except Exception:
        return LOCATION_OPTIONS

LOCATION_OPTIONS_ALL = _get_locations()

# ─── API helpers ──────────────────────────────────────────────────────────────

def call_assist(payload: dict) -> dict:
    with httpx.Client(timeout=90.0) as client:
        r = client.post(f"{BACKEND_URL}/api/v1/assist", json=payload)
        r.raise_for_status()
        return r.json()


def call_audio(audio_bytes: bytes, language: str, location: str, medications: str) -> dict:
    with httpx.Client(timeout=180.0) as client:
        r = client.post(
            f"{BACKEND_URL}/api/v1/assist/audio",
            data={"language": language, "location": location, "medications": medications},
            files={"audio": ("symptoms.wav", audio_bytes, "audio/wav")},
        )
        r.raise_for_status()
        return r.json()


def call_tts(payload: dict) -> bytes:
    with httpx.Client(timeout=120.0) as client:
        r = client.post(f"{BACKEND_URL}/api/v1/voice", json=payload)
        r.raise_for_status()
        return r.content

# ─── UI helpers ───────────────────────────────────────────────────────────────

def severity_badge(severity: str, color_key: str) -> str:
    p = SEVERITY_PALETTE.get(color_key, SEVERITY_PALETTE["green"])
    return (
        f"<div style='display:inline-block;padding:0.5rem 1.2rem;"
        f"border-radius:2rem;background:{p['bg']};border:2px solid {p['border']};"
        f"color:{p['text']};font-weight:800;font-size:1.1rem;letter-spacing:0.05em;'>"
        f"{severity}</div>"
    )


def render_facility_card(f: dict) -> str:
    emergency_tag = (
        "<span style='background:#fee2e2;color:#000000;padding:2px 8px;"
        "border-radius:999px;font-size:0.75rem;font-weight:700;'>24/7 Emergency</span>"
        if str(f.get("emergency", "")).lower() == "true" else ""
    )
    return (
        f"<div style='background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;"
        f"padding:0.8rem 1rem;margin:0.4rem 0;color:#000000;'>"
        f"<b style='color:#000000;'>{f['name']}</b> {emergency_tag}<br>"
        f"<span style='color:#000000;font-size:0.9rem;'>{f['type']} · "
        f"{f['distance_km']} km away</span><br>"
        f"<span style='color:#000000;font-size:0.9rem;'>📞 {f.get('phone', 'N/A')}</span>"
        f"</div>"
    )

# ─── Page setup ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Swasthya Sathi",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
  .appview-container .main .block-container {
    max-width: 1200px;
    padding-top: 1.5rem;
  }

  .hero {
    background: linear-gradient(135deg, #ecfdf5 0%, #dbeafe 50%, #fef9c3 100%);
    border-radius: 20px;
    padding: 1.5rem 2rem;
    border: 1px solid rgba(0,0,0,0.06);
    margin-bottom: 1.2rem;
  }

  /* 🔥 MAKE ALL HERO TEXT BLACK */
  .hero h1 {
    color: #000000 !important;
  }

  .hero p {
    color: #000000 !important;
  }

  .hero span {
    color: #000000 !important;
  }

  /* 🔥 DISCLAIMER TEXT BLACK */
  .disclaimer-box {
    background: #fff7ed;
    border-left: 5px solid #f97316;
    padding: 0.9rem 1.2rem;
    border-radius: 10px;
    margin-bottom: 1rem;
    color: #000000 !important;
    font-weight: 500;
  }

  .response-card {
    background: #ffffff;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.04);
    white-space: pre-wrap;
  }

  .section-label {
    font-size: 0.78rem;
    font-weight: 700;
    color: #ffffff; /* Changed to white as requested */
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.3rem;
  }
</style>
""", unsafe_allow_html=True)

# ─── Language Selection ───────────────────────────────────────────────────────
# We need language selected before anything else to translate UI
if "language" not in st.session_state:
    st.session_state.language = "en"

# Sidebar or Top-level language toggle
language = st.selectbox("Language / भाषा", ["en", "hi"],
                        index=0 if st.session_state.language == "en" else 1,
                        format_func=lambda x: "🇬🇧 English" if x == "en" else "🇮🇳 हिन्दी",
                        key="lang_selector")
st.session_state.language = language

T = TRANSLATIONS[language]

# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <h1 style="margin:0 0 0.3rem 0;">{T['title']}</h1>
  <p style="margin:0;color:#475569;">{T['subtitle']}</p>
</div>
""", unsafe_allow_html=True)

st.markdown(f"<div class='disclaimer-box'>{DISCLAIMER}</div>", unsafe_allow_html=True)

# ─── Inputs ───────────────────────────────────────────────────────────────────
left_col, right_col = st.columns([1.3, 1], gap="large")

with left_col:
    st.markdown(T["desc_symptoms"])
    loc_col, _ = st.columns([2, 1])
    with loc_col:
        location = st.selectbox(T["loc_label"], LOCATION_OPTIONS_ALL)

    medications = st.text_input(
        T["med_label"],
        placeholder=T["med_placeholder"],
        value="",
    )
    symptoms = st.text_area(
        T["symp_label"],
        placeholder=T["symp_placeholder"],
        height=180,
    )
    submit_btn = st.button(T["analyse_btn"], type="primary", use_container_width=True)

with right_col:
    st.markdown(T["voice_input"])
    audio_value = st.audio_input(T["voice_placeholder"])
    st.caption(T["voice_caption"])
    st.markdown("---")
    st.markdown(T["emergency_title"])
    st.markdown(f"""
    - {T['ambulance']}
    - {T['women']}
    - {T['child']}
    - {T['mental']}
    """)


# ─── Processing ───────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

result = None
used_payload = None

if submit_btn and symptoms.strip():
    used_payload = {
        "symptoms": symptoms.strip(),
        "language": language,
        "medications": [m.strip() for m in medications.split(",") if m.strip()],
        "location": location,
    }
    with st.spinner(T["running_triage"]):
        try:
            result = call_assist(used_payload)
        except httpx.HTTPError as exc:
            st.error(f"⚠️ **Backend Connection Error**")
            st.warning(
                f"The frontend could not reach the FastAPI backend at `{BACKEND_URL}`. "
                "If this is a production deployment, ensure the `BACKEND_URL` environment variable "
                "is set correctly. Error details: `{exc}`"
            )

elif audio_value is not None:
    with st.spinner(T["transcribing"]):
        try:
            result = call_audio(
                audio_value.read(),
                language=language,
                location=location,
                medications=medications,
            )
            used_payload = {
                "symptoms": result.get("transcript", ""),
                "language": language,
                "medications": [m.strip() for m in medications.split(",") if m.strip()],
                "location": location,
            }
        except httpx.HTTPError as exc:
            st.error(f"⚠️ **Backend Connection Error**")
            st.warning(
                f"The frontend could not reach the FastAPI backend at `{BACKEND_URL}`. "
                "If this is a production deployment, ensure the `BACKEND_URL` environment variable "
                "is set correctly. Error details: `{exc}`"
            )

# ─── Results display ──────────────────────────────────────────────────────────
if result:
    st.session_state.history.insert(0, result)
    color = result.get("severity_color", "green")
    severity = result.get("severity", "UNKNOWN")

    st.markdown("---")
    st.markdown(T["assessment_title"])

    res_left, res_right = st.columns([1, 1], gap="large")

    with res_left:
        st.markdown(f"<div class='section-label'>{T['severity_label']}</div>", unsafe_allow_html=True)
        st.markdown(severity_badge(severity, color), unsafe_allow_html=True)

        if result.get("transcript"):
            st.info(f"🎤 Transcribed: *{result['transcript']}*")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<div class='section-label'>{T['guidance_label']}</div>", unsafe_allow_html=True)
        triage = result.get("triage", {})
        for item in triage.get("action_items", []):
            st.markdown(f"• {item}")

        drug = result.get("drug", {})
        if drug.get("warnings"):
            st.markdown("---")
            st.markdown(f"<div class='section-label'>{T['drug_warn_label']}</div>", unsafe_allow_html=True)
            overall = drug.get("overall_risk", "none")
            risk_color = {"high": "🔴", "medium": "🟡", "none": "🟢"}.get(overall, "⚪")
            st.markdown(f"{risk_color} {T['overall_risk']}: **{overall.upper()}**")
            for w in drug["warnings"][:3]:
                st.warning(f"💊 {w.get('message', '')} *(Source: {w.get('source', '')})*")
        else:
            st.markdown("---")
            st.success(T["no_drug_warn"])

    with res_right:
        routing = result.get("routing", {})
        facilities = routing.get("facilities", [])
        if facilities:
            st.markdown(f"<div class='section-label'>{T['nearest_health_label']}</div>", unsafe_allow_html=True)
            for f in facilities:
                st.markdown(render_facility_card(f), unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"<div class='section-label'>{T['voice_res_label']}</div>", unsafe_allow_html=True)
        if used_payload:
            with st.spinner(T["generating_voice"]):
                try:
                    voice_bytes = call_tts(used_payload)
                    st.audio(BytesIO(voice_bytes).read(), format="audio/mp3")
                except Exception as exc:
                    st.warning(f"Voice generation unavailable: {exc}")

    st.markdown(f"<div class='disclaimer-box' style='margin-top:1rem;'>{result.get('disclaimer', '')}</div>",
                unsafe_allow_html=True)

# ─── History ──────────────────────────────────────────────────────────────────
if len(st.session_state.history) > 1:
    st.markdown("---")
    st.markdown(T["session_history"])
    for idx, item in enumerate(st.session_state.history[1:6], start=1):
        color_key = item.get("severity_color", "green")
        p = SEVERITY_PALETTE.get(color_key, SEVERITY_PALETTE["green"])
        with st.expander(f"#{idx} — Severity: {item.get('severity', '?')}"):
            triage_data = item.get("triage", {})
            for action in triage_data.get("action_items", []):
                st.write(f"• {action}")
            st.caption(item.get("disclaimer", ""))