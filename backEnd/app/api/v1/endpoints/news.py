from fastapi import APIRouter, Query
from typing import Optional
from app.schemas.news import NewsFeedResponse
from app.services.news_aggregator import NewsAggregatorService

router = APIRouter()

@router.get("", response_model=NewsFeedResponse)
async def get_arsenal_news(
    limit: int = Query(12, ge=1, le=50, description="Maximum number of articles per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    category: Optional[str] = Query(None, description="Filter by category: 'fan_blog', 'reddit', 'broadcast', 'official'"),
    source: Optional[str] = Query(None, description="Filter by specific source name"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    search: Optional[str] = Query(None, description="Search title, summary, source, or tags"),
    refresh: bool = Query(False, description="Force fresh fetch bypassing 15-min cache")
):
    """
    Returns paginated Arsenal FC news from premier sources:
    Pain in the Arsenal, Arseblog, BBC Sport, Reddit r/Gunners, and Daily Cannon.
    """
    payload = await NewsAggregatorService.get_shuffled_feed(force_refresh=refresh)
    articles = payload["articles"]

    if category and category != "all":
        cat_clean = category.strip().lower()
        articles = [a for a in articles if a.get("source_category", "").lower() == cat_clean]

    if source:
        s_clean = source.strip().lower()
        articles = [a for a in articles if s_clean in a.get("source_name", "").lower()]

    if tag:
        t_clean = tag.strip().lower()
        articles = [
            a for a in articles
            if any(t_clean == existing_tag.lower() or t_clean in existing_tag.lower() for existing_tag in a.get("tags", []))
        ]

    if search:
        q_clean = search.strip().lower()
        articles = [
            a for a in articles
            if (
                q_clean in a.get("title", "").lower()
                or q_clean in a.get("summary", "").lower()
                or q_clean in a.get("source_name", "").lower()
                or any(q_clean in t.lower() for t in a.get("tags", []))
            )
        ]

    total = len(articles)
    paged = articles[offset : offset + limit]
    has_more = (offset + len(paged)) < total

    return NewsFeedResponse(
        total=total,
        has_more=has_more,
        sources_active=payload["sources_active"],
        cached_at=payload["cached_at"],
        articles=paged
    )
