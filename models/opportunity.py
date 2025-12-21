"""
Social opportunity data models for social media lead generation.
"""

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from enum import Enum


class Platform(str, Enum):
    """Social media platforms."""
    REDDIT = "reddit"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    NEXTDOOR = "nextdoor"
    OTHER = "other"


class OpportunityStatus(str, Enum):
    """Status of an opportunity."""
    NEW = "new"
    REVIEWED = "reviewed"
    ENGAGED = "engaged"
    RESPONDED = "responded"
    CONVERTED = "converted"
    IGNORED = "ignored"


class SocialOpportunity(BaseModel):
    """An opportunity found on social media."""

    # Platform information
    platform: Platform
    platform_id: str = Field(description="Unique ID on the platform")
    url: str = Field(description="Direct URL to the post")

    # Author information
    author: str
    author_profile_url: Optional[str] = None

    # Post content
    title: Optional[str] = None
    content: str
    full_text: str = Field(description="Combined title + content")

    # Metadata
    created_at: datetime
    discovered_at: datetime = Field(default_factory=datetime.now)

    # Platform-specific
    subreddit: Optional[str] = None  # Reddit
    group_name: Optional[str] = None  # Facebook
    num_comments: int = 0
    score: Optional[int] = None  # Reddit score/upvotes

    # Analysis
    keywords_matched: List[str] = Field(default_factory=list)
    location_mentions: List[str] = Field(default_factory=list)
    relevance_score: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description="AI-determined relevance score"
    )
    is_omaha_related: bool = False

    # Engagement
    status: OpportunityStatus = OpportunityStatus.NEW
    suggested_response: Optional[str] = None
    engagement_notes: List[str] = Field(default_factory=list)
    engaged_at: Optional[datetime] = None

    # Additional data
    raw_data: Dict = Field(default_factory=dict)

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        use_enum_values = True

    def is_high_priority(self) -> bool:
        """Check if this is a high-priority opportunity."""
        if self.relevance_score is None:
            return False
        return self.relevance_score >= 75

    def should_engage(self) -> bool:
        """Determine if we should engage with this opportunity."""
        return (
            self.status == OpportunityStatus.NEW and
            self.is_omaha_related and
            self.relevance_score is not None and
            self.relevance_score >= 60
        )

    def to_csv_row(self) -> Dict:
        """Convert to flat dictionary for CSV export."""
        return {
            'platform': self.platform,
            'url': self.url,
            'author': self.author,
            'title': self.title or '',
            'content': self.content[:200] + '...' if len(self.content) > 200 else self.content,
            'created_at': self.created_at.isoformat(),
            'discovered_at': self.discovered_at.isoformat(),
            'subreddit_or_group': self.subreddit or self.group_name or '',
            'keywords_matched': ', '.join(self.keywords_matched),
            'location_mentions': ', '.join(self.location_mentions),
            'relevance_score': self.relevance_score or 0,
            'is_omaha_related': self.is_omaha_related,
            'status': self.status,
            'suggested_response': self.suggested_response or '',
            'num_comments': self.num_comments,
            'score': self.score or 0,
        }

    def get_summary(self) -> str:
        """Get a human-readable summary of the opportunity."""
        platform_info = ""
        if self.platform == Platform.REDDIT and self.subreddit:
            platform_info = f"r/{self.subreddit}"
        elif self.platform == Platform.FACEBOOK and self.group_name:
            platform_info = self.group_name

        return f"""
OPPORTUNITY FOUND
================
Platform: {self.platform.upper()} ({platform_info})
Author: {self.author}
Posted: {self.created_at.strftime('%Y-%m-%d %H:%M')}
Relevance: {self.relevance_score}/100
URL: {self.url}

Title: {self.title or 'N/A'}

Content Preview:
{self.content[:300]}{'...' if len(self.content) > 300 else ''}

Keywords: {', '.join(self.keywords_matched)}
Omaha-Related: {'Yes' if self.is_omaha_related else 'No'}

{f'Suggested Response:\n{self.suggested_response}\n' if self.suggested_response else ''}
================
"""
