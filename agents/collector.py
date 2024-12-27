from datetime import datetime, timedelta
from typing import List
from data_models import NewsItem
import feedparser
from pydantic_ai import Agent

class CollectorAgent(Agent):
    def __init__(self, region: str, source_urls: List[str]):
        """
        Инициализирует агента с указанным регионом и списком URL для парсинга.
        """
        self.region = region
        self.source_urls = source_urls
        self.yesterday_start = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        self.yesterday_end = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    async def tool_fetch_rss(self, url: str) -> List[NewsItem]:
        """
        Парсит RSS-канал. Фильтрует новости по вчерашней дате.
        Возвращает список объектов NewsItem.
        """
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries:
            # Преобразуем дату публикации в объект datetime
            try:
                published_date = datetime(*entry.published_parsed[:6])
            except AttributeError:
                continue

            # Фильтруем записи по диапазону вчерашнего дня
            if not (self.yesterday_start <= published_date < self.yesterday_end):
                continue

            # Создаём объект NewsItem
            items.append(NewsItem(
                source=feed.feed.title,
                title=entry.title,
                description=entry.summary,
                full_text=entry.link,
                date=published_date.strftime('%Y-%m-%d %H:%M:%S'),
                region=self.region,
                url=entry.link,
                tags=None,
                category=None,
                language=None,
                sentiment=None
            ))
        return items

    async def collect_news(self) -> List[NewsItem]:
        """
        Собирает новости из всех `source_urls`, учитывая фильтр (только за вчера).
        """
        all_items = []
        for url in self.source_urls:
            items = await self.tool_fetch_rss(url)
            all_items.extend(items)
        return all_items

