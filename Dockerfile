# Use Python 3.11 slim as base image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create data directory if it doesn't exist
RUN mkdir -p data

# Expose ports for FastAPI (8000) and Streamlit (8501)
EXPOSE 8000
EXPOSE 8501

# Make start script executable
RUN chmod +x start.sh

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV BACKEND_URL=http://localhost:8000

# Start the application using the startup script
CMD ["./start.sh"]
