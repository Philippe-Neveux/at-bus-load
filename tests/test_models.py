"""
Tests for Pydantic models used to validate Auckland Transport API responses.
"""

import pytest
from pydantic import ValidationError

from at_bus_load.models import (
    StopAttributes,
    StopData,
    StopResponse,
    TripAttributes,
    TripData,
    TripResponse,
)


class TestStopModels:
    """Test cases for stop-related models."""
    
    def test_valid_stop_attributes(self):
        """Test that valid stop attributes pass validation."""
        valid_data = {
            "stop_id": "100-56c57897",
            "stop_code": "100",
            "stop_name": "Papatoetoe Train Station",
            "stop_lat": -36.97766,
            "stop_lon": 174.84925,
            "location_type": 1,
            "wheelchair_boarding": 0
        }
        
        stop_attrs = StopAttributes(**valid_data)
        assert stop_attrs.stop_id == "100-56c57897"
        assert stop_attrs.stop_code == "100"
        assert stop_attrs.stop_name == "Papatoetoe Train Station"
        assert stop_attrs.stop_lat == -36.97766
        assert stop_attrs.stop_lon == 174.84925
        assert stop_attrs.location_type == 1
        assert stop_attrs.wheelchair_boarding == 0
    
    def test_invalid_latitude(self):
        """Test that invalid latitude raises validation error."""
        invalid_data = {
            "stop_id": "100-56c57897",
            "stop_code": "100",
            "stop_name": "Test Stop",
            "stop_lat": 91.0,  # Invalid latitude
            "stop_lon": 174.84925,
            "location_type": 1,
            "wheelchair_boarding": 0
        }
        
        with pytest.raises(ValidationError) as exc_info:
            StopAttributes(**invalid_data)
        
        assert "Latitude must be between -90 and 90" in str(exc_info.value)
    
    def test_invalid_longitude(self):
        """Test that invalid longitude raises validation error."""
        invalid_data = {
            "stop_id": "100-56c57897",
            "stop_code": "100",
            "stop_name": "Test Stop",
            "stop_lat": -36.97766,
            "stop_lon": 181.0,  # Invalid longitude
            "location_type": 1,
            "wheelchair_boarding": 0
        }
        
        with pytest.raises(ValidationError) as exc_info:
            StopAttributes(**invalid_data)
        
        assert "Longitude must be between -180 and 180" in str(exc_info.value)
    
    def test_invalid_location_type(self):
        """Test that invalid location type raises validation error."""
        invalid_data = {
            "stop_id": "100-56c57897",
            "stop_code": "100",
            "stop_name": "Test Stop",
            "stop_lat": -36.97766,
            "stop_lon": 174.84925,
            "location_type": 5,  # Invalid location type
            "wheelchair_boarding": 0
        }
        
        with pytest.raises(ValidationError) as exc_info:
            StopAttributes(**invalid_data)
        
        assert "Location type must be 0, 1, 2, 3, or 4" in str(exc_info.value)
    
    def test_valid_stop_response(self):
        """Test that valid stop response passes validation."""
        valid_response = {
            "data": [
                {
                    "type": "stops",
                    "id": "100-56c57897",
                    "attributes": {
                        "stop_id": "100-56c57897",
                        "stop_code": "100",
                        "stop_name": "Papatoetoe Train Station",
                        "stop_lat": -36.97766,
                        "stop_lon": 174.84925,
                        "location_type": 1,
                        "wheelchair_boarding": 0
                    }
                }
            ]
        }
        
        response = StopResponse(**valid_response)
        assert len(response.data) == 1
        assert response.data[0].type == "stops"
        assert response.data[0].id == "100-56c57897"
        assert response.data[0].attributes.stop_name == "Papatoetoe Train Station"
    
    def test_invalid_stop_type(self):
        """Test that invalid stop type raises validation error."""
        invalid_response = {
            "data": [
                {
                    "type": "invalid_type",  # Invalid type
                    "id": "100-56c57897",
                    "attributes": {
                        "stop_id": "100-56c57897",
                        "stop_code": "100",
                        "stop_name": "Test Stop",
                        "stop_lat": -36.97766,
                        "stop_lon": 174.84925,
                        "location_type": 1,
                        "wheelchair_boarding": 0
                    }
                }
            ]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            StopResponse(**invalid_response)
        
        assert 'Type must be "stops"' in str(exc_info.value)


class TestTripModels:
    """Test cases for trip-related models."""
    
    def test_valid_trip_attributes(self):
        """Test that valid trip attributes pass validation."""
        valid_data = {
            "arrival_time": "05:35:00",
            "departure_time": "05:35:00",
            "direction_id": 1,
            "drop_off_type": 0,
            "pickup_type": 0,
            "route_id": "NX1-203",
            "service_date": "2023-06-01",
            "shape_id": "1395-27002-6be1d2b7",
            "stop_headsign": "ALBANY STN",
            "stop_id": "7036-f1ffa0be",
            "stop_sequence": 3,
            "trip_headsign": "Britomart (Lower Albert St) To Albany Station",
            "trip_id": "1395-27002-19800-2-a27d3190",
            "trip_start_time": "05:30:00"
        }
        
        trip_attrs = TripAttributes(**valid_data)
        assert trip_attrs.arrival_time == "05:35:00"
        assert trip_attrs.departure_time == "05:35:00"
        assert trip_attrs.direction_id == 1
        assert trip_attrs.route_id == "NX1-203"
        assert trip_attrs.service_date == "2023-06-01"
        assert trip_attrs.stop_sequence == 3
        assert trip_attrs.trip_id == "1395-27002-19800-2-a27d3190"
    
    def test_invalid_time_format(self):
        """Test that invalid time format raises validation error."""
        invalid_data = {
            "arrival_time": "25:35:00",  # Invalid time
            "departure_time": "05:35:00",
            "direction_id": 1,
            "drop_off_type": 0,
            "pickup_type": 0,
            "route_id": "NX1-203",
            "service_date": "2023-06-01",
            "shape_id": "1395-27002-6be1d2b7",
            "stop_headsign": "ALBANY STN",
            "stop_id": "7036-f1ffa0be",
            "stop_sequence": 3,
            "trip_headsign": "Test Trip",
            "trip_id": "1395-27002-19800-2-a27d3190",
            "trip_start_time": "05:30:00"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TripAttributes(**invalid_data)
        
        assert "Time must be in HH:MM:SS format" in str(exc_info.value)
    
    def test_invalid_date_format(self):
        """Test that invalid date format raises validation error."""
        invalid_data = {
            "arrival_time": "05:35:00",
            "departure_time": "05:35:00",
            "direction_id": 1,
            "drop_off_type": 0,
            "pickup_type": 0,
            "route_id": "NX1-203",
            "service_date": "2023/06/01",  # Invalid date format
            "shape_id": "1395-27002-6be1d2b7",
            "stop_headsign": "ALBANY STN",
            "stop_id": "7036-f1ffa0be",
            "stop_sequence": 3,
            "trip_headsign": "Test Trip",
            "trip_id": "1395-27002-19800-2-a27d3190",
            "trip_start_time": "05:30:00"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TripAttributes(**invalid_data)
        
        assert "Date must be in YYYY-MM-DD format" in str(exc_info.value)
    
    def test_invalid_direction_id(self):
        """Test that invalid direction ID raises validation error."""
        invalid_data = {
            "arrival_time": "05:35:00",
            "departure_time": "05:35:00",
            "direction_id": 2,  # Invalid direction ID
            "drop_off_type": 0,
            "pickup_type": 0,
            "route_id": "NX1-203",
            "service_date": "2023-06-01",
            "shape_id": "1395-27002-6be1d2b7",
            "stop_headsign": "ALBANY STN",
            "stop_id": "7036-f1ffa0be",
            "stop_sequence": 3,
            "trip_headsign": "Test Trip",
            "trip_id": "1395-27002-19800-2-a27d3190",
            "trip_start_time": "05:30:00"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TripAttributes(**invalid_data)
        
        assert "Direction ID must be 0 or 1" in str(exc_info.value)
    
    def test_invalid_stop_sequence(self):
        """Test that invalid stop sequence raises validation error."""
        invalid_data = {
            "arrival_time": "05:35:00",
            "departure_time": "05:35:00",
            "direction_id": 1,
            "drop_off_type": 0,
            "pickup_type": 0,
            "route_id": "NX1-203",
            "service_date": "2023-06-01",
            "shape_id": "1395-27002-6be1d2b7",
            "stop_headsign": "ALBANY STN",
            "stop_id": "7036-f1ffa0be",
            "stop_sequence": 0,  # Invalid stop sequence
            "trip_headsign": "Test Trip",
            "trip_id": "1395-27002-19800-2-a27d3190",
            "trip_start_time": "05:30:00"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TripAttributes(**invalid_data)
        
        assert "Stop sequence must be positive" in str(exc_info.value)
    
    def test_valid_trip_response(self):
        """Test that valid trip response passes validation."""
        valid_response = {
            "data": [
                {
                    "type": "stoptrips",
                    "id": "1395-27002-19800-2-a27d3190",
                    "attributes": {
                        "arrival_time": "05:35:00",
                        "departure_time": "05:35:00",
                        "direction_id": 1,
                        "drop_off_type": 0,
                        "pickup_type": 0,
                        "route_id": "NX1-203",
                        "service_date": "2023-06-01",
                        "shape_id": "1395-27002-6be1d2b7",
                        "stop_headsign": "ALBANY STN",
                        "stop_id": "7036-f1ffa0be",
                        "stop_sequence": 3,
                        "trip_headsign": "Britomart (Lower Albert St) To Albany Station",
                        "trip_id": "1395-27002-19800-2-a27d3190",
                        "trip_start_time": "05:30:00"
                    }
                }
            ]
        }
        
        response = TripResponse(**valid_response)
        assert len(response.data) == 1
        assert response.data[0].type == "stoptrips"
        assert response.data[0].id == "1395-27002-19800-2-a27d3190"
        assert response.data[0].attributes.route_id == "NX1-203"
    
    def test_invalid_trip_type(self):
        """Test that invalid trip type raises validation error."""
        invalid_response = {
            "data": [
                {
                    "type": "invalid_type",  # Invalid type
                    "id": "1395-27002-19800-2-a27d3190",
                    "attributes": {
                        "arrival_time": "05:35:00",
                        "departure_time": "05:35:00",
                        "direction_id": 1,
                        "drop_off_type": 0,
                        "pickup_type": 0,
                        "route_id": "NX1-203",
                        "service_date": "2023-06-01",
                        "shape_id": "1395-27002-6be1d2b7",
                        "stop_headsign": "ALBANY STN",
                        "stop_id": "7036-f1ffa0be",
                        "stop_sequence": 3,
                        "trip_headsign": "Test Trip",
                        "trip_id": "1395-27002-19800-2-a27d3190",
                        "trip_start_time": "05:30:00"
                    }
                }
            ]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TripResponse(**invalid_response)
        
        assert 'Type must be "stoptrips"' in str(exc_info.value) 