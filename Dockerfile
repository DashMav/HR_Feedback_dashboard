FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY project/backend/requirements.txt ./requirements.txt  
RUN pip install -r requirements.txt

# Copy backend code
COPY project/backend/ .

# Create directory for SQLite database
RUN mkdir -p /app/data && chmod -R 777 /app/data

# Expose port (HF Spaces prefers 7860 or 8080)
EXPOSE 7860

# Set environment variables
ENV DATABASE_URL=sqlite:///./data/feedback.db
ENV SECRET_KEY=your-production-secret-key-change-this

# Run the FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]