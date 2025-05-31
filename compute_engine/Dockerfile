FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy backend and model_training code
COPY ./app ./app
# COPY ../model_training ../model_training
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Expose port (default FastAPI port)
EXPOSE 8001

# Run FastAPI app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]