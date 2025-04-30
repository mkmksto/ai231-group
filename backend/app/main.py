from typing import Dict

from fastapi import FastAPI

app = FastAPI(
    title="Medical Image Classification API",
    description="API for brain tumor image classification",
    version="1.0.0",
)


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint returning API status"""
    return {"status": "online", "message": "Medical Image Classification API"}


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}
