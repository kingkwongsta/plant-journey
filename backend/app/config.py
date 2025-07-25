from pydantic_settings import BaseSettings
from typing import List, Union
from pydantic import ConfigDict, field_validator


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Allow extra environment variables to be ignored
    )
    
    # API Configuration
    app_name: str = "Plant Journey API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # CORS Configuration - can be overridden via CORS_ORIGINS env var (comma-separated)
    cors_origins: Union[str, List[str]] = [
        "http://localhost:3000",  # Local development
        "https://plant-journey.vercel.app",  # Production Vercel deployment
        "https://plant-journey-git-main-bkwongs-projects.vercel.app",  # Vercel deployment branch
        "https://plant-journey-bkwongs-projects.vercel.app",  # Vercel alternate
        "https://*.vercel.app",  # All Vercel preview deployments
    ]
    cors_credentials: bool = True
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Supabase Configuration
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_key: str = ""
    
    # Database Configuration
    database_url: str = ""
    
    # Security Configuration (for future use)
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = ""  # Optional log file path
    json_logs: bool = False  # Whether to output logs in JSON format
    slow_request_threshold: float = 1000.0  # Milliseconds
    
    # Cache Configuration
    cache_max_size: int = 1000
    cache_default_ttl: int = 300  # 5 minutes
    cache_stats_ttl: int = 180  # 3 minutes
    
    # Rate Limiting Configuration
    rate_limit_requests_per_minute: int = 60
    rate_limit_burst_limit: int = 10
    rate_limit_enabled: bool = True
    
    # File Upload Configuration
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_image_types: List[str] = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp", "image/bmp", "image/tiff"]
    max_filename_length: int = 255
    
    # Storage Configuration
    supabase_storage_bucket: str = "event-images"
    
    # Pagination Configuration
    default_page_size: int = 20
    max_page_size: int = 100
    
    # Background Tasks Configuration
    cache_cleanup_interval: int = 300  # 5 minutes
    temp_file_cleanup_interval: int = 86400  # 24 hours
    temp_file_max_age: int = 86400  # 24 hours
    
    # Health Check Configuration
    health_check_timeout: float = 5.0  # seconds
    health_check_interval: int = 60  # seconds
    
    # API Configuration
    api_title: str = "Plant Journey API"
    api_description: str = "A comprehensive API for managing plant lifecycle events and garden data"
    api_contact_name: str = "Plant Journey API"
    api_contact_email: str = "support@plant-journey.com"
    api_license_name: str = "MIT"
    api_license_url: str = "https://opensource.org/licenses/MIT"
    
    # Feature Flags
    enable_rate_limiting: bool = True
    enable_caching: bool = True
    enable_background_tasks: bool = True
    enable_detailed_logging: bool = True
    enable_performance_monitoring: bool = True

    @field_validator('cors_origins', mode='before')
    @classmethod
    def validate_cors_origins(cls, v) -> List[str]:
        """Allow CORS origins to be set via comma-separated string from env var"""
        if v is None or v == "":
            return []
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        if isinstance(v, list):
            return v
        return []


# Create a global settings instance
settings = Settings() 