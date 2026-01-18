from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import uvicorn

from routers import v1

app = FastAPI(
    title="BMW VID Lookup Service",
    description="On-demand VID lookup with caching",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1.router)

# Thread pool for running nodriver
executor = ThreadPoolExecutor(max_workers=3)

@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "BMW VID Lookup Service",
        "status": "operational",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)