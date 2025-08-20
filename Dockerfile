# Dockerfile for Cloud Run
FROM python:3.11-slim

# Security + smaller image
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run injects $PORT; our app must bind to it
CMD ["python", "main.py"]
