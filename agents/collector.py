from base_agent import BaseAgent
from data_models import NewsItem
from datetime import datetime, timedelta
import feedparser
from typing import List


class CollectorAgent(BaseAgent):
    def __init__(self, region: str, source_urls: List[str]):
        super().__init__(name="CollectorAgent")
        self.region = region
        self.source_urls = source_urls
        self.yesterday_start = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        self.yesterday_end = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    async def process(self, data=None) -> List[NewsItem]:
        await self.log("Starting news collection...")
        all_items = []
        for url in self.source_urls:
            items = await self.tool_fetch_rss(url)
            all_items.extend(items)
        await self.log(f"Collected {len(all_items)} news items.")
        return all_items

    async def tool_fetch_rss(self, url: str) -> List[NewsItem]:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries:
            try:
                published_date = datetime(*entry.published_parsed[:6])
            except AttributeError:
                continue

            if self.yesterday_start <= published_date < self.yesterday_end:
                items.append(NewsItem(
                    source=feed.feed.title,
                    title=entry.title,
                    description=entry.summary,
                    full_text=entry.link,
                    date=published_date.strftime('%Y-%m-%d %H:%M:%S'),
                    region=self.region,
                    url=entry.link,
                ))
        return items

