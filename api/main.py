from __future__ import annotations

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from agents.orchestrator import SwasthyaSathiGraph
from api.config import get_settings
from api.dependencies import get_graph
from api.models import AssistRequest, AssistResponse
from api.voice import synthesize_speech, transcribe_audio

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "Voice-first rural health assistant for safe triage, drug checks, and nearby care routing. "
        "This system is not a diagnostic tool."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name}


@app.post("/api/v1/assist", response_model=AssistResponse)
def assist(request: AssistRequest, graph: SwasthyaSathiGraph = Depends(get_graph)) -> AssistResponse:
    response = graph.invoke(
        symptoms=request.symptoms,
        language=request.language,
        location=request.location,
        medications=request.medications,
    )
    return AssistResponse(**response)


@app.post("/api/v1/assist/audio", response_model=AssistResponse)
async def assist_audio(
    audio: UploadFile = File(...),
    language: str = Form(default="en"),
    location: str = Form(default="Sehore"),
    medications: str = Form(default=""),
    graph: SwasthyaSathiGraph = Depends(get_graph),
) -> AssistResponse:
    if not audio.content_type or "audio" not in audio.content_type:
        raise HTTPException(status_code=400, detail="Please upload a valid audio file.")
    transcript = transcribe_audio(await audio.read())
    response = graph.invoke(
        symptoms=transcript,
        language=language,
        location=location,
        medications=[item.strip() for item in medications.split(",") if item.strip()],
    )
    response["transcript"] = transcript
    return AssistResponse(**response)


@app.post("/api/v1/voice")
async def voice_response(
    request: AssistRequest,
    graph: SwasthyaSathiGraph = Depends(get_graph),
) -> Response:
    response = graph.invoke(
        symptoms=request.symptoms,
        language=request.language,
        location=request.location,
        medications=request.medications,
    )
    audio_bytes = synthesize_speech(response["message"], request.language)
    return Response(content=audio_bytes, media_type="audio/mpeg")


@app.exception_handler(Exception)
async def generic_exception_handler(_, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "detail": "A safe fallback was triggered. Please consult a doctor or nearby clinic.",
            "error": str(exc),
        },
    )
