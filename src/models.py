from typing import Optional
from pydantic import BaseModel, Field

class VehicleSelectionRequest(BaseModel):
    """Request model for vehicle selection"""
    series: str = Field(..., description="Series code (e.g., F32N)")
    body: Optional[str] = Field(None, description="Body type code")
    model: Optional[str] = Field(None, description="Model (e.g., 440i)")
    steering: Optional[str] = Field(None, description="Steering (R/L)")
    production: Optional[str] = Field(None, description="Production date")
    market: Optional[str] = Field(None, description="Market (EUR, USA, etc.)")
    engine: Optional[str] = Field(None, description="Engine code")


class VIDInfo(BaseModel):
    """VID information"""
    vid: str = Field(..., description="Complete VID string")
    series: str = Field(..., description="Series (e.g., F32)")
    url: str = Field(..., description="RealOEM URL")
    cached: bool = Field(..., description="Whether this was cached or fetched")
