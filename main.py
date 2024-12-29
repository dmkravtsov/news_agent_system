import asyncio
from agents.collector import CollectorAgent
from agents.manager import ManagerAgent
from agents.writer import WriterAgent  # Подключаем WriterAgent
from typing import List
from data_models import NewsItem, NewsDigest
from pydantic_ai import RunContext

# Списки RSS-источников для разных регионов
RSS_URL_WORLD = "https://feeds.bbci.co.uk/news/world/rss.xml"
RSS_URL_ASIA = "https://feeds.bbci.co.uk/news/world/asia/rss.xml"

async def main():
    # Создание агентов
    print("Создаём агенты для сбора новостей...")
    collector_world = CollectorAgent(region="World", source_urls=[RSS_URL_WORLD])
    collector_asia = CollectorAgent(region="Asia", source_urls=[RSS_URL_ASIA])
    manager_agent = ManagerAgent()
    writer_agent = WriterAgent()
    print("Агенты успешно созданы.")

    # Сбор новостей
    try:
        print("Начинаем сбор новостей...")
        news_world: List[NewsItem] = await collector_world.collect_news()
        news_asia: List[NewsItem] = await collector_asia.collect_news()
        print(f"Собрано {len(news_world)} новостей для региона World.")
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
            messages=all_news,
            tool_name="filter_and_analyze",
            model=None
        )
        filtered_news: List[NewsItem] = await manager_agent.filter_and_analyze(ctx)
        print("Анализ новостей завершен.")
    except Exception as e:
        print(f"Error during news filtering and analysis: {e}")
        return

    # Генерация итогового дайджеста
    try:
        print("Передача новостей в WriterAgent для создания дайджеста...")
        digest: NewsDigest = await writer_agent.create_digest(filtered_news)
        print("Дайджест успешно создан.")

        # Вывод итогового дайджеста
        print("Generated Digest:")
        print(f"Date Generated: {digest.date_generated}")
        print(f"Region: {digest.region}")
        print("Summary:")
        print(digest.summary)
    except Exception as e:
        print(f"Error during digest generation: {e}")
        return

if __name__ == "__main__":
    asyncio.run(main())
