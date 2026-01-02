# Lightweight container for the analysis FastAPI service
FROM python:3.11-slim

WORKDIR /app

# Install Java (required for PySpark)
RUN apt-get update && apt-get install -y default-jdk && rm -rf /var/lib/apt/lists/*

# Set Java environment variables
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH=$JAVA_HOME/bin:$PATH

# Use root unified requirements; build with context at project root
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy project code (analysis engine and service)
COPY analysis /app/analysis
COPY analysis_service /app/analysis_service

ENV PYTHONPATH=/app

EXPOSE 8000
CMD ["uvicorn", "analysis_service.app:app", "--host", "0.0.0.0", "--port", "8000"]
