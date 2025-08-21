# Use lightweight Python base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose port for Cloud Run
ENV PORT=8080
EXPOSE 8080

# Run the app
CMD ["python", "main.py"]
