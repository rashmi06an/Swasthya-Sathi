# Swasthya Sathi — Agentic Rural Health Assistant 🩺

> **Medical Safety Disclaimer:** Swasthya Sathi is a triage **support tool only**. It does **not** diagnose disease and does **not** replace a qualified doctor. Always consult a licensed healthcare professional. If symptoms are severe or life-threatening, seek emergency care immediately.

---

## Overview

Swasthya Sathi (स्वास्थ्य साथी — "Health Companion") is a production-ready, voice-first AI healthcare assistant designed for rural India. It accepts symptoms in **English or Hindi** (voice or text), runs them through a multi-agent LangGraph pipeline, and returns:

- 🔴 Safe triage severity: **LOW / MEDIUM / HIGH / EMERGENCY**
- 💊 Drug interaction warnings (OpenFDA + local fallback)
- 🏥 Nearest healthcare facilities by location
- 🔊 Voice response in English or Hindi (gTTS)

---

## Architecture

```
User Input (Text / Voice)
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│              FastAPI Backend  (api/main.py)               │
│  ┌──────────────────────────────────────────────────────┐ │
│  │           LangGraph Orchestrator                     │ │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  │ │
│  │  │ Triage Agent│→ │  Drug Agent  │→ │Route Agent │  │ │
│  │  │  (RAG+FAISS)│  │ (OpenFDA+    │  │(Haversine  │  │ │
│  │  │  WHO Guide  │  │  local DB)   │  │  + CSV)    │  │ │
│  │  └─────────────┘  └──────────────┘  └────────────┘  │ │
│  │                          │                           │ │
│  │                   Finalize Node                      │ │
│  │              (assemble JSON response)                │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                           │
│  Voice Pipeline:                                          │
│    Input  → Whisper (HuggingFace) → transcript           │
│    Output → gTTS → audio/mp3 bytes                       │
└───────────────────────────────────────────────────────────┘
        │
        ▼
Streamlit Frontend (frontend/app.py)
  - Chat interface + voice button
  - Language toggle (EN / HI)
  - Severity colour badges
  - Audio playback
```

### Agent Flow

```
START
  │
  ▼
[triage] ── Rule-based severity + RAG retrieval from WHO guidelines
  │
  ▼
[drug]   ── OpenFDA label lookup + local interaction database
  │
  ▼
[routing]── Haversine distance to nearest facilities from CSV
  │
  ▼
[finalize]─ Compose bilingual response + disclaimer
  │
  ▼
END
```

---

## Project Structure

```
swasthya-sathi/
├── agents/
│   ├── __init__.py
│   ├── drug_agent.py         # OpenFDA + local drug interaction agent
│   ├── orchestrator.py       # LangGraph StateGraph wiring
│   ├── prompts.py            # Safety prompts + bilingual strings
│   ├── routing_agent.py      # Haversine nearest-facility routing
│   ├── state.py              # TypedDict graph state
│   └── triage_agent.py       # Severity classification + RAG
├── api/
│   ├── __init__.py
│   ├── config.py             # Pydantic-settings configuration
│   ├── dependencies.py       # FastAPI DI: builds & caches the graph
│   ├── main.py               # FastAPI routes
│   ├── models.py             # Pydantic request/response schemas
│   └── voice.py              # Whisper STT + gTTS TTS
├── data/
│   ├── healthcare_facilities.csv   # 30 rural MP facilities with GPS
│   ├── sample_cases.json           # 15 evaluation test cases
│   └── who_guidelines.md           # WHO-style triage guidelines (RAG source)
├── evaluation/
│   ├── __init__.py
│   └── evaluate.py           # End-to-end evaluation with metrics
├── frontend/
│   ├── __init__.py
│   └── app.py                # Streamlit UI
├── rag/
│   ├── __init__.py
│   └── retriever.py          # FAISS vectorstore + HuggingFace embeddings
├── .dockerignore
├── .env.example
├── Dockerfile
├── README.md
├── requirements.txt
└── start.sh
```

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.11+ |
| pip | 24+ |
| ffmpeg | any (for Whisper audio decoding) |
| Docker | 24+ (optional, for containerised run) |
| RAM | 4 GB minimum (8 GB recommended) |
| Disk | ~3 GB (for models downloaded on first run) |

---

## Local Setup (without Docker)

### 1. Clone and enter project

```bash
git clone https://github.com/YOUR_USERNAME/swasthya-sathi.git
cd swasthya-sathi
```

### 2. Create virtual environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate      # Linux / macOS
# .venv\Scripts\activate       # Windows
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **Note:** `torch` download is ~800 MB. On first run, Whisper (`openai/whisper-tiny`, ~150 MB) and the sentence-transformer model (`all-MiniLM-L6-v2`, ~90 MB) will also be downloaded automatically.

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env if you need to change ports or model names
```

### 5. Install system dependency (ffmpeg)

```bash
# Ubuntu / Debian
sudo apt-get install -y ffmpeg

# macOS (Homebrew)
brew install ffmpeg

# Windows: download from https://ffmpeg.org/download.html and add to PATH
```

### 6. Start backend (FastAPI)

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend API docs: http://localhost:8000/docs

### 7. Start frontend (Streamlit)

Open a new terminal:

```bash
source .venv/bin/activate
streamlit run frontend/app.py --server.port 8501
```

Frontend: http://localhost:8501

---

## Docker (Recommended for Demo)

### Build

```bash
docker build -t swasthya-sathi .
```

### Run

```bash
docker run -p 8000:8000 -p 8501:8501 swasthya-sathi
```

Both services start automatically. Access:
- 🖥️ **UI:** http://localhost:8501
- 🔌 **API:** http://localhost:8000/docs

### With custom environment variables

```bash
docker run \
  -p 8000:8000 -p 8501:8501 \
  -e WHISPER_MODEL=openai/whisper-base \
  -e DEFAULT_LANGUAGE=hi \
  swasthya-sathi
```

---

## API Reference

### `POST /api/v1/assist` — Text symptoms

```bash
curl -X POST http://localhost:8000/api/v1/assist \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": "high fever for 3 days, dizziness, weakness",
    "language": "en",
    "location": "sehore",
    "medications": ["paracetamol"]
  }'
```

**Response:**
```json
{
  "severity": "HIGH",
  "severity_color": "orange",
  "message": "Severity: HIGH\n\nSeek urgent medical evaluation...",
  "disclaimer": "This assistant does not provide a diagnosis...",
  "triage": { ... },
  "drug": { "overall_risk": "none", "warnings": [] },
  "routing": { "facilities": [ { "name": "Sehore District Hospital", "distance_km": 0.0, ... } ] }
}
```

### `POST /api/v1/assist/audio` — Voice symptoms

```bash
curl -X POST http://localhost:8000/api/v1/assist/audio \
  -F "audio=@symptoms.wav" \
  -F "language=en" \
  -F "location=sehore" \
  -F "medications=paracetamol,ibuprofen"
```

### `POST /api/v1/voice` — Get audio response

Returns `audio/mpeg` bytes of the response spoken in the requested language.

### `GET /health`

```json
{ "status": "ok", "app": "Swasthya Sathi" }
```

---

## Severity Classification

| Level | Color | Action |
|---|---|---|
| LOW | 🟢 Green | Monitor at home, rest and hydrate |
| MEDIUM | 🟡 Yellow | Visit doctor/clinic within 24 hours |
| HIGH | 🟠 Orange | Urgent evaluation today |
| EMERGENCY | 🔴 Red | Go to emergency room immediately |

---

## Evaluation

Run the built-in evaluation suite against 15 hand-crafted test cases:

```bash
# From project root (with venv active)
python -m evaluation.evaluate

# Single case
python -m evaluation.evaluate --case TC001

# JSON output (for CI pipelines)
python -m evaluation.evaluate --json
```

Expected output (targets):

```
  Severity Accuracy : ≥ 90%
  Drug Risk Accuracy: ≥ 90%
  Disclaimer Rate   : 100%
  Avg Latency       : < 3000ms (CPU)
```

---

## Example Inputs / Outputs

### English — Emergency

**Input:** `"chest pain radiating to left arm, can't breathe, sweating"`

**Output:**
```
Severity: EMERGENCY

This needs emergency care right now.
Go to the nearest emergency facility or contact local emergency support immediately.

Medication warnings: No medications provided.

Nearby care options:
Sehore District Hospital (District Hospital) - 0.0 km - 07562-224100
...

⚠️ This assistant does not provide a diagnosis. For any concern, consult a licensed doctor.
```

---

### Hindi — Medium

**Input:** `"बुखार है, खांसी हो रही है, थोड़ा चक्कर भी आ रहा है"`

**Output:**
```
गंभीरता: MEDIUM

24 घंटे के भीतर डॉक्टर या क्लिनिक में जांच कराएं।
अगर बुखार, सांस की दिक्कत, कमजोरी या उलझन बढ़े तो तुरंत मदद लें।
...
```

---

### Drug Interaction Warning

**Input:** symptoms=`"mild headache"`, medications=`["ibuprofen", "warfarin"]`

**Output:**
```
Severity: LOW

Medication warnings: This combination may increase bleeding risk.
Risk level: high | Source: local_fallback
```

---

## Deployment on HuggingFace Spaces

1. Create a new Space → choose **Docker** SDK
2. Push the repository
3. Set environment variables in Space Settings:
   - `API_PORT=7860` (HF Spaces uses port 7860)
   - `STREAMLIT_PORT=8501`
   - `BACKEND_URL=http://localhost:7860`
4. Update `Dockerfile` `EXPOSE` line to `7860 8501` if needed

> **Note:** HF Spaces free tier has 16 GB RAM — sufficient for this project. Model downloads are cached across restarts.

---

## Configuration Reference

| Variable | Default | Description |
|---|---|---|
| `API_PORT` | `8000` | FastAPI port |
| `STREAMLIT_PORT` | `8501` | Streamlit port |
| `BACKEND_URL` | `http://localhost:8000` | URL Streamlit uses to reach API |
| `WHISPER_MODEL` | `openai/whisper-tiny` | STT model (tiny/base/small) |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | RAG embedding model |
| `OPENFDA_BASE_URL` | `https://api.fda.gov/drug/label.json` | OpenFDA endpoint |
| `DEFAULT_LANGUAGE` | `en` | Default response language |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Run tests: `python -m evaluation.evaluate`
4. Submit a pull request

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Acknowledgements

- WHO Primary Healthcare Guidelines
- OpenFDA (free public drug label API)
- HuggingFace Transformers + Whisper
- LangChain + LangGraph
- Streamlit
- Government of India — National Health Mission rural health data
