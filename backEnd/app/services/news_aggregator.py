import asyncio
import datetime
import hashlib
import random
import re
import urllib.request
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional

class NewsAggregatorService:
    _cache: Optional[Dict[str, Any]] = None
    _cache_time: Optional[datetime.datetime] = None
    CACHE_DURATION_MINUTES = 15

    SOURCES = [
        {
            "name": "Pain in the Arsenal",
            "url": "https://paininthearsenal.com/feed/",
            "category": "fan_blog",
            "color": "#EF0107",
            "type": "rss"
        },
        {
            "name": "Arseblog News",
            "url": "https://arseblog.news/feed/",
            "category": "fan_blog",
            "color": "#D4AF37",
            "type": "rss"
        },
        {
            "name": "BBC Sport Arsenal",
            "url": "https://feeds.bbci.co.uk/sport/football/teams/arsenal/rss.xml",
            "category": "broadcast",
            "color": "#FFD700",
            "type": "rss"
        },
        {
            "name": "Daily Cannon",
            "url": "https://dailycannon.com/feed/",
            "category": "fan_blog",
            "color": "#C8102E",
            "type": "rss"
        },
        {
            "name": "Reddit r/Gunners",
            "url": "https://www.reddit.com/r/Gunners/top/.rss?t=week",
            "category": "reddit",
            "color": "#FF4500",
            "type": "atom"
        }
    ]

    ENTITY_TAG_PATTERNS = [
        # Players & Staff
        (r"\b(saka|bukayo)\b", "Saka"),
        (r"\b(odegaard|ødegaard)\b", "Ødegaard"),
        (r"\b(saliba|william saliba)\b", "Saliba"),
        (r"\b(gabriel magalh[aã]es|gabriel dos santos)\b", "Gabriel"),
        (r"\b(jesus|gabriel jesus)\b", "Jesus"),
        (r"\b(rice|declan rice)\b", "Rice"),
        (r"\b(havertz|kai havertz)\b", "Havertz"),
        (r"\b(martinelli|gabriel martinelli)\b", "Martinelli"),
        (r"\b(trossard|leandro trossard)\b", "Trossard"),
        (r"\b(calafiori|riccardo)\b", "Calafiori"),
        (r"\b(timber|jurrien timber)\b", "Timber"),
        (r"\b(ben white)\b", "Ben White"),
        (r"\b(merino|mikel merino)\b", "Merino"),
        (r"\b(partey|thomas partey)\b", "Partey"),
        (r"\b(nwaneri|ethan nwaneri)\b", "Nwaneri"),
        (r"\b(raya|david raya)\b", "Raya"),
        (r"\b(sterling|raheem sterling)\b", "Sterling"),
        (r"\b(arteta|mikel arteta)\b", "Arteta"),

        # Competitions
        (r"\b(champions league|ucl)\b", "UCL"),
        (r"\b(premier league|epl)\b", "Premier League"),
        (r"\b(fa cup)\b", "FA Cup"),
        (r"\b(carabao|league cup)\b", "Carabao Cup"),
        (r"\b(spurs|tottenham|north london derby|nld)\b", "North London Derby"),

        # Tactical & Media Topics
        (r"\b(tactics|tactical|formation|compactness|press|low block)\b", "Tactics"),
        (r"\b(lineup|starting xi|team news|selection|dugout)\b", "Lineup"),
        (r"\b(injury|injuries|fitness|knock|hamstring|recovery)\b", "Injuries"),
        (r"\b(transfer|transfers|rumor|signing|scout|clause|bid)\b", "Transfers"),
        (r"\b(fans|supporters|emirates|ashburton|atmosphere|crowd)\b", "Supporters")
    ]

    @classmethod
    def extract_tags(cls, title: str, summary: str = "") -> List[str]:
        """Extract high-signal entity and domain tags from headline and summary."""
        combined_text = f"{title} {summary}".lower()
        extracted: List[str] = []
        for pattern, tag in cls.ENTITY_TAG_PATTERNS:
            if re.search(pattern, combined_text, re.IGNORECASE):
                if tag not in extracted:
                    extracted.append(tag)
        if not extracted:
            extracted = ["Arsenal", "First Team"]
        return extracted[:4]

    @classmethod
    def _clean_html(cls, raw_html: Optional[str]) -> str:
        if not raw_html:
            return ""
        clean = re.sub(r"<[^>]+>", " ", raw_html)
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean[:280] + ("..." if len(clean) > 280 else "")

    @classmethod
    def _extract_image(cls, item: ET.Element, raw_content: str) -> Optional[str]:
        # 1. Media content / enclosure
        for child in item:
            if child.tag.endswith("enclosure") and child.attrib.get("type", "").startswith("image"):
                return child.attrib.get("url")
            if child.tag.endswith("content") and child.attrib.get("medium") == "image":
                return child.attrib.get("url")
            if child.tag.endswith("thumbnail"):
                return child.attrib.get("url")
        # 2. Extract first <img> tag from HTML content/description
        img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', raw_content)
        if img_match:
            return img_match.group(1)
        return None

    @classmethod
    def _fetch_source_sync(cls, source_cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
        articles: List[Dict[str, Any]] = []
        try:
            req = urllib.request.Request(
                source_cfg["url"],
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 GunnersPortal/1.0"
                }
            )
            with urllib.request.urlopen(req, timeout=4.5) as response:
                xml_bytes = response.read()
                root = ET.fromstring(xml_bytes)

                if source_cfg["type"] == "atom":
                    # Reddit Atom feed
                    entries = root.findall(".//{http://www.w3.org/2005/Atom}entry")
                    for entry in entries[:15]:
                        title_el = entry.find("{http://www.w3.org/2005/Atom}title")
                        link_el = entry.find("{http://www.w3.org/2005/Atom}link")
                        updated_el = entry.find("{http://www.w3.org/2005/Atom}updated")
                        content_el = entry.find("{http://www.w3.org/2005/Atom}content")

                        title = title_el.text if title_el is not None and title_el.text else "Top r/Gunners Discussion"
                        link = link_el.attrib.get("href", "") if link_el is not None else ""
                        pub_time = updated_el.text if updated_el is not None else datetime.datetime.utcnow().isoformat()
                        raw_content = content_el.text if content_el is not None and content_el.text else ""
                        summary = cls._clean_html(raw_content) or "Top discussion and supporter reactions from the r/Gunners community."
                        img = cls._extract_image(entry, raw_content)

                        # Skip automated bot mod sticky posts
                        if "Daily Discussion" in title and "Free Talk" in title:
                            continue

                        h = hashlib.md5(link.encode()).hexdigest()[:10]
                        articles.append({
                            "id": f"art_reddit_{h}",
                            "title": title,
                            "summary": summary,
                            "source_name": source_cfg["name"],
                            "source_category": source_cfg["category"],
                            "source_color": source_cfg["color"],
                            "article_url": link,
                            "image_url": img,
                            "published_at": pub_time,
                            "author": "r/Gunners Community",
                            "tags": cls.extract_tags(title, summary)
                        })
                else:
                    # Standard RSS Feed
                    items = root.findall(".//item")
                    for it in items[:15]:
                        title_el = it.find("title")
                        link_el = it.find("link")
                        pub_el = it.find("pubDate")
                        desc_el = it.find("description")

                        title = title_el.text if title_el is not None and title_el.text else "Arsenal News Update"
                        link = link_el.text if link_el is not None and link_el.text else ""
                        pub_time = pub_el.text if pub_el is not None else datetime.datetime.utcnow().isoformat()
                        raw_desc = desc_el.text if desc_el is not None and desc_el.text else ""
                        summary = cls._clean_html(raw_desc) or "Latest Arsenal news and tactical analysis."
                        img = cls._extract_image(it, raw_desc)

                        h = hashlib.md5((link or title).encode()).hexdigest()[:10]
                        articles.append({
                            "id": f"art_{source_cfg['category']}_{h}",
                            "title": title,
                            "summary": summary,
                            "source_name": source_cfg["name"],
                            "source_category": source_cfg["category"],
                            "source_color": source_cfg["color"],
                            "article_url": link,
                            "image_url": img,
                            "published_at": pub_time,
                            "author": source_cfg["name"],
                            "tags": cls.extract_tags(title, summary)
                        })
        except Exception as e:
            # Individual source failures insulated gracefully
            pass
        return articles

    @classmethod
    async def get_shuffled_feed(cls, force_refresh: bool = False) -> Dict[str, Any]:
        now = datetime.datetime.utcnow()
        if (
            not force_refresh
            and cls._cache
            and cls._cache_time
            and (now - cls._cache_time).total_seconds() < cls.CACHE_DURATION_MINUTES * 60
        ):
            return cls._cache

        # Run feed downloads asynchronously across threadpool
        loop = asyncio.get_running_loop()
        tasks = [loop.run_in_executor(None, cls._fetch_source_sync, src) for src in cls.SOURCES]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_articles: List[Dict[str, Any]] = []
        active_sources: List[str] = []

        for idx, res in enumerate(results):
            if isinstance(res, list) and res:
                all_articles.extend(res)
                active_sources.append(cls.SOURCES[idx]["name"])

        # Fallback curated Arsenal items if internet is cold
        if not all_articles:
            all_articles = cls._get_baseline_articles()
            active_sources = ["Pain in the Arsenal", "Arseblog News", "BBC Sport Arsenal"]

        # Interweave / shuffle across sources to prevent a single publisher monopolizing top spots
        random.seed(42)  # Deterministic shuffle per batch
        random.shuffle(all_articles)

        cached_payload = {
            "total": len(all_articles),
            "sources_active": active_sources,
            "cached_at": now,
            "articles": all_articles
        }

        cls._cache = cached_payload
        cls._cache_time = now
        return cached_payload

    @classmethod
    def _get_baseline_articles(cls) -> List[Dict[str, Any]]:
        now = datetime.datetime.utcnow().isoformat()
        return [
            {
                "id": "art_base_1",
                "title": "Arsenal tactical evolution: How Mikel Arteta created European-elite defensive compactness",
                "summary": "Deep dive into Arsenal's defensive structure, double pivot spacing, and pressing triggers at Emirates Stadium.",
                "source_name": "Arseblog News",
                "source_category": "fan_blog",
                "source_color": "#D4AF37",
                "article_url": "https://arseblog.news",
                "image_url": "https://crests.football-data.org/57.png",
                "published_at": now,
                "author": "Tactical Analyst",
                "tags": ["Arteta", "Tactics", "Supporters"]
            },
            {
                "id": "art_base_2",
                "title": "Why Bukayo Saka's half-space combinations unlock stubborn 5-man low blocks",
                "summary": "Analyzing the right-sided triangles between Ben White, Martin Ødegaard, and Bukayo Saka.",
                "source_name": "Pain in the Arsenal",
                "source_category": "fan_blog",
                "source_color": "#EF0107",
                "article_url": "https://paininthearsenal.com",
                "image_url": "https://crests.football-data.org/57.png",
                "published_at": now,
                "author": "Arsenal Staff",
                "tags": ["Saka", "Ødegaard", "Ben White", "Tactics"]
            },
            {
                "id": "art_base_3",
                "title": "Match Preview: Crucial Premier League clash at Emirates Stadium this weekend",
                "summary": "Team news, predicted starting lineups, head-to-head records, and press conference quotes.",
                "source_name": "BBC Sport Arsenal",
                "source_category": "broadcast",
                "source_color": "#FFD700",
                "article_url": "https://www.bbc.com/sport/football/teams/arsenal",
                "image_url": "https://crests.football-data.org/57.png",
                "published_at": now,
                "author": "BBC Sport",
                "tags": ["Premier League", "Lineup", "Supporters"]
            }
        ]
