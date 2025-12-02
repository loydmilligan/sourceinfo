# Multi-stage Dockerfile for SourceInfo

# ============================================
# Stage 1: Build the React frontend
# ============================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/web

# Copy package files
COPY web/package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY web/ ./

# Build the frontend
RUN npm run build

# ============================================
# Stage 2: Production image with API + static files
# ============================================
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy API code
COPY api/ ./api/

# Copy database
COPY data/sources.db ./data/sources.db

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/web/dist ./static

# Create a simple server that serves both API and static files
RUN pip install --no-cache-dir aiofiles

# Environment variables
ENV DB_PATH=/app/data/sources.db
ENV API_HOST=0.0.0.0
ENV API_PORT=8000

# Expose port
EXPOSE 8000

# Run the API server
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
