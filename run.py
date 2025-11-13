"""
Clean runner without emoji logging issues
"""
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("Starting Room Designer AI API")
    print("=" * 60)
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )