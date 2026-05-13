# Use Python 3.11 slim
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for Hugging Face
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy requirements and install
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy everything
COPY --chown=user . .

# Expose ports
EXPOSE 7860
EXPOSE 8000

# Ensure start script is executable
RUN chmod +x start.sh

# Start the application
CMD ["./start.sh"]
