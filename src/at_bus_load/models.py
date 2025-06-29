"""
Pydantic models for validating Auckland Transport API responses.
"""

import logging
from datetime import date, time
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

# Set up logger
logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.WARNING)


class StopAttributes(BaseModel):
    """Model for stop attributes in the API response."""
    
    stop_id: str = Field(description="Unique identifier for the stop")
    stop_code: str = Field(description="Public-facing stop code")
    stop_name: str = Field(description="Name of the stop")
    stop_lat: float = Field(description="Latitude coordinate of the stop")
    stop_lon: float = Field(description="Longitude coordinate of the stop")
    location_type: int = Field(description="Type of location (1 for stops)")
    wheelchair_boarding: int = Field(description="Wheelchair accessibility (0 or 1)")
    
    @field_validator('stop_lat')
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        """Validate latitude is within valid range."""
        if not -90 <= v <= 90:
            logger.warning(f'Latitude {v} is outside valid range (-90 to 90), but continuing with value')
        return v
    
    @field_validator('stop_lon')
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        """Validate longitude is within valid range."""
        if not -180 <= v <= 180:
            logger.warning(f'Longitude {v} is outside valid range (-180 to 180), but continuing with value')
        return v


class StopData(BaseModel):
    """Model for individual stop data in the API response."""
    
    type: str = Field(description="Type of the data object")
    id: str = Field(description="Unique identifier")
    attributes: StopAttributes = Field(description="Stop attributes")
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate that the type is 'stops'."""
        if v != 'stop':
            logger.warning(f'Expected type "stop" but got "{v}", but continuing with value')
        return v


class StopResponse(BaseModel):
    """Model for the complete stops API response."""
    
    data: List[StopData] = Field(description="List of stop data objects")


class TripAttributes(BaseModel):
    """Model for trip attributes in the API response."""
    
    arrival_time: str = Field(description="Arrival time in HH:MM:SS format")
    departure_time: str = Field(description="Departure time in HH:MM:SS format")
    direction_id: int = Field(description="Direction identifier (0 or 1)")
    drop_off_type: int = Field(description="Drop-off type (0, 1, 2, or 3)")
    pickup_type: int = Field(description="Pickup type (0, 1, 2, or 3)")
    route_id: str = Field(description="Route identifier")
    service_date: str = Field(description="Service date in YYYY-MM-DD format")
    shape_id: str = Field(description="Shape identifier")
    stop_headsign: str = Field(description="Stop headsign")
    stop_id: str = Field(description="Stop identifier")
    stop_sequence: int = Field(description="Stop sequence number")
    trip_headsign: str = Field(description="Trip headsign")
    trip_id: str = Field(description="Trip identifier")
    trip_start_time: str = Field(description="Trip start time in HH:MM:SS format")
    
    @field_validator('arrival_time', 'departure_time', 'trip_start_time')
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        """Validate time format is HH:MM:SS."""
        try:
            time.fromisoformat(v)
        except ValueError:
            logger.warning(f'Time "{v}" is not in HH:MM:SS format, but continuing with value')
        return v
    
    @field_validator('service_date')
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date format is YYYY-MM-DD."""
        try:
            date.fromisoformat(v)
        except ValueError:
            logger.warning(f'Date "{v}" is not in YYYY-MM-DD format, but continuing with value')
        return v
    
    @field_validator('stop_sequence')
    @classmethod
    def validate_stop_sequence(cls, v: int) -> int:
        """Validate stop sequence is positive."""
        if v <= 0:
            logger.warning(f'Stop sequence {v} is not positive, but continuing with value')
        return v


class TripData(BaseModel):
    """Model for individual trip data in the API response."""
    
    type: str = Field(description="Type of the data object")
    id: str = Field(description="Unique identifier")
    attributes: TripAttributes = Field(description="Trip attributes")
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate that the type is 'stoptrips'."""
        if v != 'stoptrip':
            logger.warning(f'Expected type "stoptrip" but got "{v}", but continuing with value')
        return v


class TripResponse(BaseModel):
    """Model for the complete trips API response."""
    
    data: List[TripData] = Field(description="List of trip data objects") 