# from base_agent import BaseAgent
# from data_models import NewsItem
# from datetime import datetime, timedelta
# import feedparser
# from typing import List


# class CollectorAgent(BaseAgent):
#     def __init__(self, region: str, source_urls: List[str]):
#         super().__init__(name="CollectorAgent")
#         self.region = region
#         self.source_urls = source_urls
#         self.yesterday_start = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
#         self.yesterday_end = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

#     async def process(self, data=None) -> List[NewsItem]:
#         await self.log("Starting news collection...")
#         all_items = []
#         for url in self.source_urls:
#             items = await self.tool_fetch_rss(url)
#             all_items.extend(items)
#         await self.log(f"Collected {len(all_items)} news items.")
#         return all_items

#     async def tool_fetch_rss(self, url: str) -> List[NewsItem]:
#         feed = feedparser.parse(url)
#         items = []
#         for entry in feed.entries:
#             try:
#                 published_date = datetime(*entry.published_parsed[:6])
#             except AttributeError:
#                 continue

#             if self.yesterday_start <= published_date < self.yesterday_end:
#                 items.append(NewsItem(
#                     source=feed.feed.title,
#                     title=entry.title,
#                     description=entry.summary,
#                     full_text=entry.link,
#                     date=published_date.strftime('%Y-%m-%d %H:%M:%S'),
#                     region=self.region,
#                     url=entry.link,
#                 ))
#         return items

from base_agent import BaseAgent
from data_models import NewsItem
from datetime import datetime, timedelta
import feedparser
from typing import List

class CollectorAgent(BaseAgent):
    def __init__(self, region: str, source_urls: List[str], days_ago: int = 0):
        """
        Инициализация агента для сбора новостей.

        :param region: Регион, для которого собираются новости.
        :param source_urls: Список URL-источников.
        :param days_ago: Количество дней назад, за которые нужно собирать данные (включительно).
        """
        super().__init__(name="CollectorAgent")
        self.region = region
        self.source_urls = source_urls
        self.days_ago = days_ago
        self.start_date, self.end_date = self._calculate_date_range()

    def _calculate_date_range(self):
        """
        Вычисляет временной диапазон на основе параметра days_ago.
        days_ago=0 - только сегодня, =1 - сегодня и вчера
        :return: (start_date, end_date) — начальная и конечная даты.
        """
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = today - timedelta(days=self.days_ago)
        end_date = today + timedelta(days=1) - timedelta(seconds=1)  # Сегодня до конца дня
        return start_date, end_date

    async def process(self, data=None) -> List[NewsItem]:
        """
        Собирает и фильтрует новости в указанном временном диапазоне.

        :param data: Дополнительные данные (не используются).
        :return: Список объектов NewsItem.
        """
        await self.log("Starting news collection...")
        all_items = []
        for url in self.source_urls:
            items = await self.tool_fetch_rss(url)
            all_items.extend(items)
        await self.log(f"Collected {len(all_items)} news items.")
        return all_items

    async def tool_fetch_rss(self, url: str) -> List[NewsItem]:
        """
        Парсит RSS-канал и фильтрует новости по временному диапазону.

        :param url: URL RSS-канала.
        :return: Список объектов NewsItem.
        """
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries:
            try:
                published_date = datetime(*entry.published_parsed[:6])
            except AttributeError:
                continue

            # Фильтруем записи по диапазону дат
            if self.start_date <= published_date <= self.end_date:
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
