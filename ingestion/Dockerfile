FROM python:3.11-slim

WORKDIR /app

# Install from unified root requirements; build with context at project root
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy only ingestion module into image
COPY ingestion /app/ingestion
ENV PYTHONPATH=/app
WORKDIR /app/ingestion

ENTRYPOINT ["python", "main.py"]
