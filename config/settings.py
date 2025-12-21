"""
Configuration settings for the construction lead generation system.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )

    # API Keys
    anthropic_api_key: str = Field(..., description="Anthropic API key for Claude")
    serper_api_key: Optional[str] = Field(None, description="Serper API key for Google search")
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key (optional)")

    # Social Media Credentials
    reddit_client_id: Optional[str] = Field(None, description="Reddit API client ID")
    reddit_client_secret: Optional[str] = Field(None, description="Reddit API client secret")
    reddit_username: Optional[str] = Field(None, description="Reddit username")
    reddit_password: Optional[str] = Field(None, description="Reddit password")

    # Business Information
    business_name: str = Field("Your Construction Company", description="Business name")
    business_phone: Optional[str] = Field(None, description="Business phone number")
    business_email: Optional[str] = Field(None, description="Business email")
    business_website: Optional[str] = Field(None, description="Business website")
    services: str = Field(
        "tile work, bathroom remodeling, kitchen renovation, flooring",
        description="Services offered (comma-separated)"
    )

    # Target Location Settings
    target_city: str = Field("Omaha", description="Target city name")
    target_state: str = Field("NE", description="Target state abbreviation")
    target_radius_miles: float = Field(35.0, description="Search radius in miles")
    target_lat: float = Field(41.2565, description="Omaha latitude")
    target_lon: float = Field(-95.9345, description="Omaha longitude")

    # Lead Generation Settings
    max_leads_per_run: int = Field(25, description="Maximum leads to generate per run")
    min_lead_score: int = Field(60, ge=0, le=100, description="Minimum score for qualified lead")
    output_directory: str = Field("./output", description="Directory for output files")

    # Search Settings
    search_depth: str = Field(
        "moderate",
        description="Search depth: quick, moderate, thorough"
    )
    concurrent_searches: int = Field(3, ge=1, le=10, description="Number of concurrent searches")

    # Database Settings
    database_url: str = Field(
        "sqlite:///./leads.db",
        description="Database connection URL"
    )

    # Logging
    log_level: str = Field("INFO", description="Logging level")
    log_file: str = Field("./logs/lead_generation.log", description="Log file path")

    # Model Settings
    claude_model: str = Field("claude-sonnet-4-5-20250929", description="Claude model to use")

    # Engagement Settings
    auto_engage: bool = Field(False, description="Enable automatic engagement/commenting")
    engagement_delay_min: int = Field(30, description="Minimum minutes between engagements")
    engagement_daily_limit: int = Field(10, description="Maximum engagements per day")

    def get_target_coordinates(self) -> tuple[float, float]:
        """Get target location coordinates as (lat, lon) tuple."""
        return (self.target_lat, self.target_lon)

    def get_target_location_str(self) -> str:
        """Get target location as formatted string."""
        return f"{self.target_city}, {self.target_state}"


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment."""
    global _settings
    _settings = Settings()
    return _settings
