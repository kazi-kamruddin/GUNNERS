from fastapi import APIRouter, Query
from typing import Optional, List
from app.schemas.news import NewsFeedResponse, NewsItemResponse
from app.services.news_aggregator import NewsAggregatorService

router = APIRouter()

@router.get("", response_model=NewsFeedResponse)
async def get_arsenal_news(
    category: Optional[str] = Query(None, description="Filter by category: 'fan_blog', 'reddit', 'broadcast'"),
    source: Optional[str] = Query(None, description="Filter by specific source name"),
    refresh: bool = Query(False, description="Force fresh fetch bypassing 15-min cache")
):
    """
    Returns aggregated Arsenal news from premier sources:
    Pain in the Arsenal, Arseblog, BBC Sport, Reddit r/Gunners top of the week, and Daily Cannon.
    All articles are balanced, shuffled, and link directly to original publishers.
    """
    payload = await NewsAggregatorService.get_shuffled_feed(force_refresh=refresh)
    articles = payload["articles"]

    if category and category != "all":
        articles = [a for a in articles if a["source_category"] == category]

    if source:
        s_clean = source.strip().lower()
        articles = [a for a in articles if s_clean in a["source_name"].lower()]

    return NewsFeedResponse(
        total=len(articles),
        sources_active=payload["sources_active"],
        cached_at=payload["cached_at"],
        articles=articles
    )
