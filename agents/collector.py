import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import aiohttp
import feedparser
from pydantic import Field
from base_agent import BaseAgent
from data_models import NewsItem

class CollectorAgent(BaseAgent):
    """
    Агент для сбора данных из RSS-лент.
    """
    region: str = Field(..., description="Регион, для которого собираются новости")
    source_urls: List[str] = Field(..., description="Список URL-источников")
    days_ago: int = Field(default=0, description="Количество дней назад, за которые нужно собрать данные")

    @property
    def start_date(self) -> datetime:
        return (datetime.now() - timedelta(days=self.days_ago)).replace(hour=0, minute=0, second=0, microsecond=0)

    @property
    def end_date(self) -> datetime:
        return datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)

    async def process(self) -> List[NewsItem]:
        """
        Основной метод обработки данных.
        :return: Список объектов NewsItem.
        """
        await self.log("Starting news collection...")
        all_items = []
        for url in self.source_urls:
            items = await self.tool_fetch_rss(url)
            all_items.extend(items)

        await self.log(f"Collected {len(all_items)} news items.")
        # Преобразование словарей в объекты NewsItem
        news_items = [NewsItem(**item) for item in all_items]
        return news_items

    async def tool_fetch_rss(self, url: str) -> List[Dict[str, Any]]:
        """
        Загружает RSS-ленту, обрабатывает и возвращает список новостей.
        :param url: URL RSS-ленты.
        :return: Список новостей в виде словарей.
        """
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    content = await response.read()
                    feed = feedparser.parse(content)
        except Exception as e:
            await self.log(f"Error fetching RSS feed from {url}: {e}", level="WARNING")
            return []

        items = []
        for entry in feed.entries:
            try:
                published_date = datetime(*entry.published_parsed[:6])
                if self.start_date <= published_date <= self.end_date:
                    items.append({
                        "source": feed.feed.title,
                        "title": entry.title,
                        "description": entry.summary,
                        "date": published_date,
                        "region": self.region,
                        "url": entry.link,
                        "tags": [],
                        "category": None,
                        "language": None,
                        "sentiment": None,
                    })
            except Exception as e:
                await self.log(f"Error processing entry in {url}: {e}", level="WARNING")
        return items
