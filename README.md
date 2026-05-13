---
title: Swasthya Sathi
emoji: 🩺
colorFrom: yellow
colorTo: blue
sdk: docker
pinned: false
---

# Swasthya Sathi — Agentic Rural Health Assistant 🩺

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/Rashmi2608/swasthya-sathi)

**Live Demo:** [https://huggingface.co/spaces/Rashmi2608/swasthya-sathi](https://huggingface.co/spaces/Rashmi2608/swasthya-sathi)

**Medical Safety Disclaimer:** Swasthya Sathi is a triage **support tool only**. It does **not** diagnose disease and does **not** replace a qualified doctor. Always consult a licensed healthcare professional. If symptoms are severe or life-threatening, seek emergency care immediately.

---

## Overview

Swasthya Sathi (स्वास्थ्य साथी — "Health Companion") is a production-ready, voice-first AI healthcare assistant designed for rural India. It accepts symptoms in **English or Hindi** (voice or text), runs them through a multi-agent LangGraph pipeline, and returns:

1.  **Severity Assessment**: (LOW, MEDIUM, HIGH, EMERGENCY)
2.  **Actionable Guidance**: Home remedies for minor issues or clinical steps for more serious ones.
3.  **Drug Interaction Warnings**: Safety checks for medications being taken by the user.
4.  **Healthcare Routing**: Recommends the nearest healthcare facilities (PHCs, hospitals) based on the user's district.

## Features

- **Voice First**: Built-in audio recording and transcription (Whisper) for low-literacy accessibility.
- **Multilingual**: Full support for English and Hindi throughout the UI and agent logic.
- **Agentic RAG**: Uses a medical RAG pipeline based on WHO and local health guidelines.
- **Local Context**: Database of Indian districts and healthcare facilities.
- **Premium UI**: Modern, responsive dashboard with dark mode support and glassmorphism aesthetics.

## Tech Stack

- **Backend**: FastAPI
- **Agents**: LangChain + LangGraph
- **Frontend**: Streamlit
- **Data**: FAISS (Vector DB), Sentence-Transformers
- **Deployment**: Docker on **Hugging Face Spaces**

## How to Run Locally

1.  Clone the repository.
2.  Create a virtual environment: `python -m venv venv`.
3.  Install dependencies: `pip install -r requirements.txt`.
4.  Run the startup script: `./start.sh`.
5.  Access the app at `http://localhost:7860`.

---
*Created for the Advanced Agentic Coding project.*
