import sqlite3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from dependencies.VIDDatabase import VIDDatabase
from dependencies.VIDFetcher import VIDFetcher
from models import VehicleSelectionRequest, VIDInfo
from typing import Optional

db = VIDDatabase()

#app = APIRouter()
router = APIRouter()

@router.post("/api/v1/lookup-vid", response_model=VIDInfo)
async def lookup_vid(selection: VehicleSelectionRequest):
    """
    Lookup VID based on vehicle selection
    Returns cached VID if available, otherwise fetches from RealOEM
    """
    try:
        # Check cache first
        cached = db.get_vid(
            series=selection.series,
            body=selection.body,
            model=selection.model,
            market=selection.market,
            production=selection.production,
            engine=selection.engine,
            steering=selection.steering
        )
        
        if cached:
            print(f"Cache hit for {selection.series}")
            return VIDInfo(
                vid=cached['vid'],
                series=cached['series'],
                url=cached['url'],
                cached=True
            )
        
        # Not in cache, fetch from RealOEM
        print(f"Cache miss, fetching from RealOEM...")
        vid_data = await VIDFetcher.fetch_vid(selection)
        
        # Check if vid_data is None
        if not vid_data or vid_data is None:
            raise HTTPException(
                status_code=404,
                detail="VID not found for the given selection. Please verify your selection criteria."
            )
        
        # Save to cache
        db.save_vid(vid_data)
        
        return VIDInfo(
            vid=vid_data['vid'],
            series=vid_data['series'],
            url=vid_data['url'],
            cached=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in lookup_vid: {e}")
        import traceback
        traceback.print_exc()  # Add this for full stack trace
        raise HTTPException(
            status_code=500,
            detail=f"Lookup failed: {str(e)}"
        )


@router.get("/api/v1/cache-stats")
async def get_cache_stats():
    """Get cache statistics"""
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM vid_cache")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT series, COUNT(*) FROM vid_cache GROUP BY series")
    by_series = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    
    return {
        "total_cached": total,
        "by_series": by_series
    }
