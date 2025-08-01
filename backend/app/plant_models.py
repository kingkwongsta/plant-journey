from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import Optional, List, Any, Dict, Union
from datetime import datetime, date
from uuid import UUID, uuid4
from enum import Enum
import re

from app.validators import InputSanitizer, InputValidator


# Enums for plant journey system
class EventType(str, Enum):
    HARVEST = "harvest"
    BLOOM = "bloom"
    SNAPSHOT = "snapshot"


class PlantStatus(str, Enum):
    ACTIVE = "active"
    HARVESTED = "harvested"
    DECEASED = "deceased"
    DORMANT = "dormant"


class PlantCategory(str, Enum):
    VEGETABLE = "vegetable"
    FRUIT = "fruit"
    FLOWER = "flower"
    HERB = "herb"
    TREE = "tree"
    SHRUB = "shrub"
    OTHER = "other"


# BloomStage enum removed - no longer used in simplified bloom events


# Plant Variety Models
class PlantVarietyBase(BaseModel):
    """Base model for plant variety data"""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the plant variety")
    category: PlantCategory = Field(..., description="Category of the plant variety")
    description: Optional[str] = Field(None, max_length=2000, description="Description of the plant variety")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and sanitize variety name"""
        return InputSanitizer.sanitize_crop_name(v)
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate and sanitize description field"""
        if v is None:
            return None
        return InputSanitizer.sanitize_notes(v)


class PlantVarietyCreate(PlantVarietyBase):
    """Model for creating a plant variety"""
    pass


class PlantVarietyUpdate(BaseModel):
    """Model for updating a plant variety"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[PlantCategory] = None
    description: Optional[str] = Field(None, max_length=2000)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate and sanitize variety name"""
        if v is None:
            return None
        return InputSanitizer.sanitize_crop_name(v)
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate and sanitize description field"""
        if v is None:
            return None
        return InputSanitizer.sanitize_notes(v)


class PlantVariety(PlantVarietyBase):
    """Complete plant variety model with all fields"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the plant variety")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the variety was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the variety was last updated")


# Plant Models
class PlantBase(BaseModel):
    """Base model for plant data"""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the individual plant")
    variety_id: Optional[UUID] = Field(None, description="ID of the plant variety")
    planted_date: Optional[date] = Field(None, description="Date when the plant was planted")
    status: PlantStatus = Field(default=PlantStatus.ACTIVE, description="Current status of the plant")
    notes: Optional[str] = Field(None, max_length=2000, description="Additional notes about the plant")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and sanitize plant name"""
        return InputSanitizer.sanitize_crop_name(v)
    
    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        """Validate and sanitize notes"""
        if v is None:
            return None
        return InputSanitizer.sanitize_notes(v)


class PlantCreate(PlantBase):
    """Model for creating a plant"""
    pass


class PlantUpdate(BaseModel):
    """Model for updating a plant"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    variety_id: Optional[UUID] = None
    planted_date: Optional[date] = None
    status: Optional[PlantStatus] = None
    notes: Optional[str] = Field(None, max_length=2000)


class Plant(PlantBase):
    """Complete plant model with all fields"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the plant")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the plant was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the plant was last updated")
    variety: Optional[Any] = Field(None, description="Associated plant variety (legacy field)")
    events: List['PlantEvent'] = Field(default_factory=list, description="Events associated with this plant")


# Event-specific data models
class HarvestEventData(BaseModel):
    """Data specific to harvest events"""
    plant_variety: str = Field(..., min_length=1, max_length=100, description="Type of plant variety harvested")
    quantity: float = Field(..., gt=0, description="Quantity harvested")
    
    @field_validator('plant_variety')
    @classmethod
    def validate_plant_variety(cls, v: str) -> str:
        """Validate and sanitize plant variety name"""
        return InputSanitizer.sanitize_crop_name(v)
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: Any) -> float:
        """Validate quantity value"""
        return InputValidator.validate_quantity(v)


class BloomEventData(BaseModel):
    """Data specific to bloom events"""
    plant_variety: Optional[str] = Field(None, max_length=100, description="Plant variety name (auto-populated from plant)")
    plant_variety_id: Optional[UUID] = Field(None, description="Optional plant variety ID from form selection")
    
    @field_validator('plant_variety')
    @classmethod
    def validate_plant_variety(cls, v: Optional[str]) -> Optional[str]:
        """Validate and sanitize plant variety"""
        if v is None:
            return None
        return InputSanitizer.sanitize_string(v, max_length=100)


class SnapshotEventData(BaseModel):
    """Data specific to snapshot events"""
    # Snapshot events now only use the base fields (description, location, images)
    # No additional specific fields needed
    pass


# Import weather models from weather module to avoid duplication
from app.weather import WeatherData, Coordinates


# Plant Event Models
class PlantEventBase(BaseModel):
    """Base model for plant event data"""
    plant_id: Optional[UUID] = Field(None, description="ID of the associated plant")
    event_type: EventType = Field(..., description="Type of event")
    event_date: datetime = Field(..., description="Date and time of the event")
    description: Optional[str] = Field(None, max_length=2500, description="Event description and notes")
    location: Optional[str] = Field(None, max_length=200, description="Location where event occurred")
    coordinates: Optional[Coordinates] = Field(None, description="GPS coordinates for weather data")
    
    @field_validator('event_date')
    @classmethod
    def validate_event_date(cls, v: Any) -> datetime:
        """Validate event date"""
        if isinstance(v, str):
            return InputValidator.validate_datetime(v, 'event_date')
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate and sanitize description field"""
        if v is None:
            return None
        return InputSanitizer.sanitize_notes(v)
    
    @field_validator('location')
    @classmethod
    def validate_location(cls, v: Optional[str]) -> Optional[str]:
        """Validate and sanitize location"""
        if v is None:
            return None
        return InputSanitizer.sanitize_location(v)


# Specific event creation models
class HarvestEventCreate(PlantEventBase, HarvestEventData):
    """Model for creating harvest events"""
    event_type: EventType = Field(default=EventType.HARVEST, description="Event type (automatically set to harvest)")


class BloomEventCreate(PlantEventBase, BloomEventData):
    """Model for creating bloom events"""
    event_type: EventType = Field(default=EventType.BLOOM, description="Event type (automatically set to bloom)")


class SnapshotEventCreate(PlantEventBase, SnapshotEventData):
    """Model for creating snapshot events"""
    event_type: EventType = Field(default=EventType.SNAPSHOT, description="Event type (automatically set to snapshot)")


# Union type for dynamic event creation
PlantEventCreate = Union[HarvestEventCreate, BloomEventCreate, SnapshotEventCreate]


class PlantEventUpdate(BaseModel):
    """Model for updating plant events"""
    plant_id: Optional[UUID] = None
    event_date: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=2500)
    location: Optional[str] = Field(None, max_length=200)
    
    # Event-specific fields (only relevant fields will be used based on event_type)
    quantity: Optional[float] = Field(None, gt=0)
    plant_variety: Optional[str] = Field(None, max_length=100)
    
    @field_validator('event_date')
    @classmethod
    def validate_event_date(cls, v: Any) -> Optional[datetime]:
        """Validate event date"""
        if v is None:
            return None
        if isinstance(v, str):
            from app.validators import InputValidator
            return InputValidator.validate_datetime(v, 'event_date')
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate and sanitize description field"""
        if v is None:
            return None
        from app.validators import InputSanitizer
        return InputSanitizer.sanitize_notes(v)
    
    @field_validator('location')
    @classmethod
    def validate_location(cls, v: Optional[str]) -> Optional[str]:
        """Validate and sanitize location"""
        if v is None:
            return None
        from app.validators import InputSanitizer
        return InputSanitizer.sanitize_location(v)
    
    @field_validator('plant_variety')
    @classmethod
    def validate_plant_variety(cls, v: Optional[str]) -> Optional[str]:
        """Validate and sanitize plant variety"""
        if v is None:
            return None
        from app.validators import InputSanitizer
        return InputSanitizer.sanitize_string(v, max_length=100)
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: Optional[float]) -> Optional[float]:
        """Validate quantity value"""
        if v is None:
            return None
        from app.validators import InputValidator
        return InputValidator.validate_quantity(v)


class PlantEvent(PlantEventBase):
    """Complete plant event model with all fields"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the event")
    user_id: Optional[UUID] = Field(None, description="ID of the user who created the event")
    
    # Event-specific fields (nullable based on event type)
    quantity: Optional[float] = Field(None, description="Quantity harvested (harvest events only)")
    plant_variety: Optional[str] = Field(None, description="Plant variety name (all event types)")
    weather: Optional[WeatherData] = Field(None, description="Weather data at the time of the event")
    
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the event was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the event was last updated")
    images: List['EventImage'] = Field(default_factory=list, description="Associated images for this event")
    plant: Optional[Plant] = Field(None, description="Associated plant")


# Event Image Models (replaces HarvestImage)
class EventImageBase(BaseModel):
    """Base model for event image data"""
    filename: str = Field(..., min_length=1, max_length=255, description="Generated filename in storage")
    original_filename: str = Field(..., min_length=1, max_length=255, description="Original filename from upload")
    file_path: str = Field(..., min_length=1, max_length=500, description="Full path in storage")
    file_size: int = Field(..., gt=0, description="File size in bytes")
    mime_type: str = Field(..., min_length=1, max_length=100, description="MIME type of the file")
    width: Optional[int] = Field(None, gt=0, description="Image width in pixels")
    height: Optional[int] = Field(None, gt=0, description="Image height in pixels")
    upload_order: int = Field(default=0, ge=0, description="Order of image in upload sequence")
    
    @field_validator('filename', 'original_filename')
    @classmethod
    def validate_filenames(cls, v: str) -> str:
        """Validate and sanitize filenames"""
        try:
            sanitized = InputSanitizer.sanitize_string(v, max_length=255)
            
            # Check for dangerous characters in filename
            if re.search(r'[<>:"|?*\x00-\x1f]', sanitized):
                from app.exceptions import ValidationException
                raise ValidationException("Filename contains invalid characters")
            
            return sanitized
        except Exception:
            # For existing data that might not pass validation, return as-is but truncated
            return v[:255] if len(v) > 255 else v
    
    @field_validator('file_path')
    @classmethod
    def validate_file_path(cls, v: str) -> str:
        """Validate file path"""
        sanitized = InputSanitizer.sanitize_string(v, max_length=500)
        
        # Basic path validation - should not contain dangerous patterns
        if '..' in sanitized or sanitized.startswith('/'):
            from app.exceptions import ValidationException
            raise ValidationException("Invalid file path")
        
        return sanitized
    
    @field_validator('file_size')
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        """Validate file size"""
        max_size = 10 * 1024 * 1024  # 10MB
        if v > max_size:
            from app.exceptions import ValidationException
            raise ValidationException(f"File too large: {v} bytes > {max_size} bytes")
        
        if v < 100:
            from app.exceptions import ValidationException
            raise ValidationException("File too small or corrupted")
        
        return v
    
    @field_validator('mime_type')
    @classmethod
    def validate_mime_type(cls, v: str) -> str:
        """Validate MIME type"""
        allowed_types = {
            'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 
            'image/webp', 'image/bmp', 'image/tiff'
        }
        
        if v.lower() not in allowed_types:
            from app.exceptions import ValidationException
            raise ValidationException(f"Invalid MIME type: {v}")
        
        return v.lower()


class EventImageCreate(EventImageBase):
    """Model for creating an event image"""
    event_id: UUID = Field(..., description="ID of the associated plant event")


class EventImageUpdate(BaseModel):
    """Model for updating an event image"""
    upload_order: Optional[int] = Field(None, ge=0, description="Order of image in upload sequence")


class EventImage(EventImageBase):
    """Complete event image model with all fields"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the event image")
    event_id: UUID = Field(..., description="ID of the associated plant event")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the image was uploaded")
    updated_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the image was last updated")
    public_url: Optional[str] = Field(default=None, description="Public URL for accessing the image")


class PlantVarietyResponse(BaseModel):
    """Response model for plant variety operations"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[PlantVariety] = Field(None, description="The plant variety data if applicable")


class PlantVarietyListResponse(BaseModel):
    """Response model for plant variety list operations"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: List[PlantVariety] = Field(default_factory=list, description="List of plant varieties")
    total: int = Field(..., description="Total number of plant varieties")


class PlantResponse(BaseModel):
    """Response model for plant operations"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Plant] = Field(None, description="The plant data if applicable")


class PlantListResponse(BaseModel):
    """Response model for plant list operations"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: List[Plant] = Field(default_factory=list, description="List of plants")
    total: int = Field(..., description="Total number of plants")


class PlantEventResponse(BaseModel):
    """Response model for plant event operations"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[PlantEvent] = Field(None, description="The plant event data if applicable")


class PlantEventListResponse(BaseModel):
    """Response model for plant event list operations"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: List[PlantEvent] = Field(default_factory=list, description="List of plant events")
    total: int = Field(..., description="Total number of plant events")


class EventImageResponse(BaseModel):
    """Response model for event image operations"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[EventImage] = Field(None, description="The event image data if applicable")


class EventStats(BaseModel):
    """Event statistics model"""
    total_events: int = Field(..., description="Total number of events")
    this_month: int = Field(..., description="Events created this month")
    this_week: int = Field(..., description="Events created this week")
    harvest_events: int = Field(..., description="Total harvest events")
    bloom_events: int = Field(..., description="Total bloom events")
    snapshot_events: int = Field(..., description="Total snapshot events")


class EventStatsResponse(BaseModel):
    """Response model for event statistics operations"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[EventStats] = Field(None, description="The event statistics data")


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = Field(default=False, description="Always false for errors")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")


# Helper functions for dynamic model selection
def get_event_create_model(event_type: str):
    """Get the appropriate event creation model based on event type"""
    if event_type == EventType.HARVEST:
        return HarvestEventCreate
    elif event_type == EventType.BLOOM:
        return BloomEventCreate
    elif event_type == EventType.SNAPSHOT:
        return SnapshotEventCreate
    else:
        raise ValueError(f"Unknown event type: {event_type}")


def validate_event_data(event_type: str, data: dict):
    """Validate event data based on event type"""
    model_class = get_event_create_model(event_type)
    return model_class(**data)


# Forward reference resolution
PlantEvent.model_rebuild()
Plant.model_rebuild()
EventImage.model_rebuild()