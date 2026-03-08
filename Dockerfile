# COE892 Decentralized Cryptocurrency - Backend + Frontend
# Lab 4-5: Containers
FROM python:3.11-slim

WORKDIR /app

# Install deps
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Generate gRPC code (proto is in backend)
COPY backend/ /app/backend/
WORKDIR /app/backend
RUN python generate_grpc.py

# Frontend static files
COPY frontend/ /app/frontend/

WORKDIR /app/backend
ENV PYTHONPATH=/app/backend
EXPOSE 8000 50051

# Run API only by default (gRPC can run in same process via run.py)
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
