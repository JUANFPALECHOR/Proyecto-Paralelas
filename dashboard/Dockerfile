FROM python:3.11-slim

WORKDIR /app

# Install from unified root requirements; build context must be repo root
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY dashboard /app/dashboard
ENV PYTHONPATH=/app

EXPOSE 8501
CMD ["streamlit", "run", "dashboard/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
