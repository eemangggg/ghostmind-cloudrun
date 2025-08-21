FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
EXPOSE 8080

# IMPORTANT: "main:app" must match main.py's Flask app object name.
CMD exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 2 --threads 4 --timeout 0 main:app
