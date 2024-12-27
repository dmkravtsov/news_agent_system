import asyncio
from agents.collector import CollectorAgent
from agents.manager import ManagerAgent
from typing import List
from data_models import NewsItem
from pydantic_ai import RunContext

# Списки RSS-источников для разных регионов
RSS_URL_WORLD = "https://feeds.bbci.co.uk/news/world/rss.xml"
RSS_URL_ASIA = "https://feeds.bbci.co.uk/news/world/asia/rss.xml"

async def main():
    # Создание агентов для разных регионов
    print("Создаём агенты для сбора новостей...")
    collector_world = CollectorAgent(region="World", source_urls=[RSS_URL_WORLD])
    collector_asia = CollectorAgent(region="Asia", source_urls=[RSS_URL_ASIA])
    manager_agent = ManagerAgent()
    print("Агенты успешно созданы.")

    # Сбор новостей
    try:
        print("Начинаем сбор новостей...")
        news_world: List[NewsItem] = await collector_world.collect_news()
        print(f"Собрано {len(news_world)} новостей для региона World.")
        news_asia: List[NewsItem] = await collector_asia.collect_news()
        print(f"Собрано {len(news_asia)} новостей для региона Asia.")
    except Exception as e:
        print(f"Error during news collection: {e}")
        return

    # Объединение новостей
    all_news = news_world + news_asia
    print(f"Всего собрано {len(all_news)} новостей.")

    # Обработка новостей менеджером
    try:
        print("Передача новостей в ManagerAgent для анализа...")
        ctx = RunContext(
            deps=None,
            retry=False,
            messages=all_news,  # Передаём новости в messages вместо input_data
            tool_name="filter_and_analyze",
            model=None
        )
        filtered_news: List[NewsItem] = await manager_agent.filter_and_analyze(ctx)
        print("Анализ новостей завершен.")
    except Exception as e:
        print(f"Error during news filtering and analysis: {e}")
        return

    # Вывод результатов
    if filtered_news:
        print(f"Processed {len(filtered_news)} news items:")
        for news in filtered_news:
            print(f"Title: {news.title}")
            print(f"Description: {news.description}")
            print(f"Date: {news.date}")
            print(f"Region: {news.region}")
            print(f"Source: {news.source}")
            print(f"Link: {news.full_text}")
            print(f"Category: {news.category}")
            print(f"Language: {news.language}")
            print(f"Sentiment: {news.sentiment}")
            print(f"Tags: {', '.join(news.tags or [])}")
            print("-" * 50)
    else:
        print("No news items were processed.")

if __name__ == "__main__":
    asyncio.run(main())

