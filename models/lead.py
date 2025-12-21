"""
Lead data models for construction lead generation system.
"""

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class ProjectType(str, Enum):
    """Types of construction projects."""
    COMMERCIAL = "commercial"
    RESIDENTIAL = "residential"
    INDUSTRIAL = "industrial"
    INFRASTRUCTURE = "infrastructure"
    RENOVATION = "renovation"
    NEW_BUILD = "new_build"
    MIXED_USE = "mixed_use"
    UNKNOWN = "unknown"


class LeadStatus(str, Enum):
    """Status of a lead in the pipeline."""
    NEW = "new"
    QUALIFIED = "qualified"
    CONTACTED = "contacted"
    IN_DISCUSSION = "in_discussion"
    PROPOSAL_SENT = "proposal_sent"
    WON = "won"
    LOST = "lost"
    DISQUALIFIED = "disqualified"


class LeadSource(str, Enum):
    """Source where the lead was discovered."""
    BUILDING_PERMIT = "building_permit"
    COMMERCIAL_LISTING = "commercial_listing"
    GOVERNMENT_CONTRACT = "government_contract"
    NEWS_ARTICLE = "news_article"
    BUSINESS_EXPANSION = "business_expansion"
    REAL_ESTATE_DEVELOPMENT = "real_estate_development"
    WEB_SEARCH = "web_search"
    OTHER = "other"


class ContactInfo(BaseModel):
    """Contact information for a lead."""
    name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None


class Location(BaseModel):
    """Geographic location information."""
    address: str
    city: str
    state: str
    zip_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance_from_target: Optional[float] = Field(
        None,
        description="Distance in miles from Omaha, NE"
    )

    @field_validator('distance_from_target')
    @classmethod
    def validate_distance(cls, v):
        """Ensure distance is positive."""
        if v is not None and v < 0:
            raise ValueError('Distance must be non-negative')
        return v


class ProjectDetails(BaseModel):
    """Details about the construction project."""
    project_type: ProjectType = ProjectType.UNKNOWN
    description: str
    estimated_budget: Optional[float] = None
    budget_range_min: Optional[float] = None
    budget_range_max: Optional[float] = None
    square_footage: Optional[int] = None
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    timeline_urgency: Optional[str] = Field(
        None,
        description="Urgency level: immediate, soon, planned, future"
    )
    permit_number: Optional[str] = None
    project_value: Optional[float] = None


class LeadScore(BaseModel):
    """Scoring breakdown for a lead."""
    total_score: int = Field(
        0,
        ge=0,
        le=100,
        description="Total score from 0-100"
    )
    project_size_score: int = Field(0, ge=0, le=30)
    timeline_score: int = Field(0, ge=0, le=20)
    location_score: int = Field(0, ge=0, le=20)
    contact_quality_score: int = Field(0, ge=0, le=15)
    company_fit_score: int = Field(0, ge=0, le=15)
    notes: List[str] = Field(default_factory=list)


class ConstructionLead(BaseModel):
    """Complete lead information for a construction opportunity."""

    # Identification
    id: Optional[str] = None
    source: LeadSource
    source_url: Optional[str] = None

    # Company and Contact
    company_name: str
    contact_info: Optional[ContactInfo] = None

    # Project Information
    project: ProjectDetails
    location: Location

    # Lead Management
    status: LeadStatus = LeadStatus.NEW
    score: Optional[LeadScore] = None

    # Metadata
    discovered_date: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    notes: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

    # Additional data
    raw_data: Dict = Field(
        default_factory=dict,
        description="Original raw data from source"
    )

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        use_enum_values = True

    def is_qualified(self, min_score: int = 60) -> bool:
        """Check if lead meets minimum qualification score."""
        if self.score is None:
            return False
        return self.score.total_score >= min_score

    def is_in_radius(self, max_distance: float = 35.0) -> bool:
        """Check if lead is within target radius."""
        if self.location.distance_from_target is None:
            return False
        return self.location.distance_from_target <= max_distance

    def to_csv_row(self) -> Dict:
        """Convert lead to flat dictionary for CSV export."""
        return {
            'id': self.id,
            'company_name': self.company_name,
            'contact_name': self.contact_info.name if self.contact_info else None,
            'contact_email': self.contact_info.email if self.contact_info else None,
            'contact_phone': self.contact_info.phone if self.contact_info else None,
            'project_type': self.project.project_type,
            'project_description': self.project.description,
            'estimated_budget': self.project.estimated_budget,
            'square_footage': self.project.square_footage,
            'location_address': self.location.address,
            'location_city': self.location.city,
            'location_state': self.location.state,
            'distance_miles': self.location.distance_from_target,
            'total_score': self.score.total_score if self.score else 0,
            'status': self.status,
            'source': self.source,
            'source_url': self.source_url,
            'discovered_date': self.discovered_date.isoformat(),
            'timeline_urgency': self.project.timeline_urgency,
        }
