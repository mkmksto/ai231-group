FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy dependencies first
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# This flattens the contents of app/ into /app/
COPY app/* ./

# Expose port (default FastAPI port)
EXPOSE 8001

# Run FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]