from pydantic import BaseModel, Field
from typing import Optional, List
import datetime

class NewsItemResponse(BaseModel):
    id: str
    title: str
    summary: str
    source_name: str
    source_category: str  # 'fan_blog', 'reddit', 'broadcast', 'official'
    source_color: str     # Hex code for UI badge
    article_url: str      # Target external redirect
    image_url: Optional[str] = None
    published_at: str
    author: Optional[str] = None
    upvotes: Optional[int] = None
    tags: List[str] = Field(default_factory=list)

class NewsFeedResponse(BaseModel):
    total: int
    sources_active: List[str]
    cached_at: datetime.datetime
    articles: List[NewsItemResponse]
