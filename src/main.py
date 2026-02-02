from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn
#from v1 import router
from routers.v1 import router
#from VIDFetcher import VIDFetcher
from dependencies.VIDFetcher import VIDFetcher

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

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    """Start the browser once when the container starts"""
    await VIDFetcher.get_browser()

@app.on_event("shutdown")
async def shutdown_event():
    """Properly close the browser on shutdown"""
    if VIDFetcher._browser:
        await VIDFetcher._browser.stop()

@app.get("/")
async def root():
    return {"service": "BMW VID Lookup Service", "status": "operational"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001)