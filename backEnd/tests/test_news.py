import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_get_arsenal_news_aggregator():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/news")
        assert res.status_code == 200
        data = res.json()
        assert "articles" in data
        assert "sources_active" in data
        assert isinstance(data["articles"], list)
        assert len(data["articles"]) > 0

        first = data["articles"][0]
        assert "title" in first
        assert "article_url" in first
        assert "source_name" in first
        assert "source_category" in first
        assert "source_color" in first
        assert "tags" in first
        assert isinstance(first["tags"], list)

@pytest.mark.asyncio
async def test_filter_news_by_category():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/news?category=reddit")
        assert res.status_code == 200
        data = res.json()
        for item in data["articles"]:
            assert item["source_category"] == "reddit"

def test_entity_tag_extraction():
    from app.services.news_aggregator import NewsAggregatorService
    tags = NewsAggregatorService.extract_tags(
        "Mikel Arteta praises Bukayo Saka after Champions League masterclass",
        "Deep tactical breakdown of the right-wing dynamics and low block penetration."
    )
    assert "Arteta" in tags
    assert "Saka" in tags
    assert "UCL" in tags
    assert "Tactics" in tags
