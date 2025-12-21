"""Data models for the construction lead generation system."""

from .lead import (
    ConstructionLead,
    ContactInfo,
    Location,
    ProjectDetails,
    LeadScore,
    ProjectType,
    LeadStatus,
    LeadSource,
)

from .opportunity import (
    SocialOpportunity,
    Platform,
    OpportunityStatus,
)

__all__ = [
    'ConstructionLead',
    'ContactInfo',
    'Location',
    'ProjectDetails',
    'LeadScore',
    'ProjectType',
    'LeadStatus',
    'LeadSource',
    'SocialOpportunity',
    'Platform',
    'OpportunityStatus',
]
