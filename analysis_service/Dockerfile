# Lightweight container for the analysis FastAPI service
FROM python:3.11-slim

WORKDIR /app

# Install system deps if needed (commented to keep minimal)
# RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Use root unified requirements; build with context at project root
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy project code (analysis engine and service)
COPY analysis /app/analysis
COPY analysis_service /app/analysis_service

ENV PYTHONPATH=/app

EXPOSE 8000
CMD ["uvicorn", "analysis_service.app:app", "--host", "0.0.0.0", "--port", "8000"]
