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
    try:
        url = st.secrets.get("BACKEND_URL", None)
        if url:
            return url
    except Exception:
        pass
    return os.environ.get("BACKEND_URL", "http://localhost:8000")

BACKEND_URL = _get_backend_url()

DISCLAIMER = (
    "⚠️ Swasthya Sathi is a triage support tool only. It does **not** diagnose "
    "disease and does **not** replace a qualified doctor. Always consult a licensed "
    "healthcare professional. If symptoms are severe or life-threatening, "
    "seek emergency care immediately. **Dial 108** for ambulance."
)

LOCATION_OPTIONS = [
    "Sehore", "Ashta", "Nasrullaganj", "Ichhawar", "Rehti", "Budhni",
    "Bhopal", "Mandideep",
    "Vidisha", "Basoda", "Sironj",
    "Raisen", "Sanchi", "Obaidullaganj", "Begumganj",
]

SEVERITY_PALETTE = {
    "green":  {"bg": "#d1fae5", "border": "#10b981", "text": "#065f46"},
    "yellow": {"bg": "#fef9c3", "border": "#f59e0b", "text": "#78350f"},
    "orange": {"bg": "#ffedd5", "border": "#f97316", "text": "#7c2d12"},
    "red":    {"bg": "#fee2e2", "border": "#ef4444", "text": "#7f1d1d"},
}

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
    color: #000000; /* also black */
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.3rem;
  }
</style>
""", unsafe_allow_html=True)

# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1 style="margin:0 0 0.3rem 0;">🩺 Swasthya Sathi <span style="font-size:1rem;font-weight:400;color:#64748b;">स्वास्थ्य साथी</span></h1>
  <p style="margin:0;color:#475569;">
    Agentic rural health assistant — safe triage · drug interaction check · nearest care routing
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown(f"<div class='disclaimer-box'>{DISCLAIMER}</div>", unsafe_allow_html=True)

# ─── Inputs ───────────────────────────────────────────────────────────────────
left_col, right_col = st.columns([1.3, 1], gap="large")

with left_col:
    st.markdown("#### 📝 Describe Symptoms")
    lang_col, loc_col = st.columns(2)
    with lang_col:
        language = st.selectbox("Language / भाषा", ["en", "hi"],
                                format_func=lambda x: "🇬🇧 English" if x == "en" else "🇮🇳 हिन्दी")
    with loc_col:
        location = st.selectbox("Nearest Location", LOCATION_OPTIONS)

    medications = st.text_input(
        "Current medicines (comma-separated)",
        placeholder="e.g. paracetamol, metformin",
        value="",
    )
    symptoms = st.text_area(
        "Symptoms",
        placeholder=(
            "Example: High fever for 3 days, dizziness and body ache\n"
            "उदाहरण: 3 दिन से तेज बुखार, चक्कर और बदन दर्द"
        ),
        height=180,
    )
    submit_btn = st.button("🔍 Analyse Symptoms", type="primary", use_container_width=True)

with right_col:
    st.markdown("#### 🎤 Voice Input")
    audio_value = st.audio_input("Speak your symptoms")
    st.caption(
        "Speak in English or Hindi. Audio is transcribed using Whisper and "
        "a voice response is generated using gTTS."
    )
    st.markdown("---")
    st.markdown("#### ℹ️ Emergency Numbers")
    st.markdown("""
    - 🚑 **108** — Ambulance (national)
    - 👩 **181** — Women's helpline
    - 👶 **1098** — Child helpline
    - 🧠 **iCall: 9152987821** — Mental health
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
    with st.spinner("Running triage agents…"):
        try:
            result = call_assist(used_payload)
        except httpx.HTTPError as exc:
            st.error(f"Backend error: {exc}. Ensure FastAPI is running at {BACKEND_URL}")

elif audio_value is not None:
    with st.spinner("Transcribing audio and running triage agents…"):
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
            st.error(f"Backend error: {exc}. Ensure FastAPI is running at {BACKEND_URL}")

# ─── Results display ──────────────────────────────────────────────────────────
if result:
    st.session_state.history.insert(0, result)
    color = result.get("severity_color", "green")
    severity = result.get("severity", "UNKNOWN")

    st.markdown("---")
    st.markdown("### 📋 Assessment Result")

    res_left, res_right = st.columns([1, 1], gap="large")

    with res_left:
        st.markdown("<div class='section-label'>Severity</div>", unsafe_allow_html=True)
        st.markdown(severity_badge(severity, color), unsafe_allow_html=True)

        if result.get("transcript"):
            st.info(f"🎤 Transcribed: *{result['transcript']}*")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-label'>Guidance</div>", unsafe_allow_html=True)
        triage = result.get("triage", {})
        for item in triage.get("action_items", []):
            st.markdown(f"• {item}")

        drug = result.get("drug", {})
        if drug.get("warnings"):
            st.markdown("---")
            st.markdown("<div class='section-label'>Drug Interaction Warnings</div>", unsafe_allow_html=True)
            overall = drug.get("overall_risk", "none")
            risk_color = {"high": "🔴", "medium": "🟡", "none": "🟢"}.get(overall, "⚪")
            st.markdown(f"{risk_color} Overall risk: **{overall.upper()}**")
            for w in drug["warnings"][:3]:
                st.warning(f"💊 {w.get('message', '')} *(Source: {w.get('source', '')})*")
        else:
            st.markdown("---")
            st.success("✅ No drug interaction warnings found for provided medications.")

    with res_right:
        routing = result.get("routing", {})
        facilities = routing.get("facilities", [])
        if facilities:
            st.markdown("<div class='section-label'>Nearest Healthcare</div>", unsafe_allow_html=True)
            for f in facilities:
                st.markdown(render_facility_card(f), unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("<div class='section-label'def>Voice Response</div>", unsafe_allow_html=True)
        if used_payload:
            with st.spinner("Generating audio response…"):
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
    st.markdown("### 📜 Session History")
    for idx, item in enumerate(st.session_state.history[1:6], start=1):
        color_key = item.get("severity_color", "green")
        p = SEVERITY_PALETTE.get(color_key, SEVERITY_PALETTE["green"])
        with st.expander(f"#{idx} — Severity: {item.get('severity', '?')}"):
            triage_data = item.get("triage", {})
            for action in triage_data.get("action_items", []):
                st.write(f"• {action}")
            st.caption(item.get("disclaimer", ""))