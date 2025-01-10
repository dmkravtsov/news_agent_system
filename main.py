
import asyncio
from agents.collector import CollectorAgent  
from agents.manager import ManagerAgent  
from agents.writer import WriterAgent
from agents.publisher import PublisherAgent
from typing import List
from data_models import NewsItem, NewsDigest
import nest_asyncio

# Разрешаем повторное использование событийного цикла
nest_asyncio.apply()

# Конфигурация RSS-источников
RSS_SOURCES = [
    {"region": "World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "days_ago": 0},
    {"region": "Asia", "url": "https://feeds.bbci.co.uk/news/world/asia/rss.xml", "days_ago": 0},
    # {"region": "World", "url": "https://www.theguardian.com/world/rss", "days_ago": 0},
    # {"region": "World", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "days_ago": 0},
]

async def main():
    # Создание агентов
    print("Создаём агентов для сбора новостей...")
    collector_agents = [
        CollectorAgent(region=source["region"], source_urls=[source["url"]], days_ago=source["days_ago"])
        for source in RSS_SOURCES
    ]
    manager_agent = ManagerAgent()
    writer_agent = WriterAgent()
    publisher_agent = PublisherAgent()
    print("Агенты успешно созданы.")

    # Сбор новостей
    all_news = []
    try:
        print("Начинаем сбор новостей...")
        for collector in collector_agents:
            news: List[NewsItem] = await collector.process()
            all_news.extend(news)
            print(f"Собрано {len(news)} новостей для региона {collector.region}.")
    except Exception as e:
        print(f"Error during news collection: {e}")
        return

    print(f"Всего собрано {len(all_news)} новостей.")

    # Обработка новостей менеджером
    try:
        print("Передача новостей в ManagerAgent для анализа...")
        filtered_news: List[NewsItem] = await manager_agent.process(all_news)
        print(f"Анализ новостей завершен. Обработано {len(filtered_news)} новостей.")
    except Exception as e:
        print(f"Error during news filtering and analysis: {e}")
        return

    # Генерация итогового дайджеста
    try:
        print("Передача новостей в WriterAgent для создания дайджеста...")
        digest: NewsDigest = await writer_agent.process(filtered_news)
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

    # Публикация в Telegram
    try:
        print("Публикация дайджеста в Telegram...")
        await publisher_agent.process(digest)  # Отправляем дайджест через PublisherAgent
        print("Дайджест успешно опубликован в Telegram.")
    except Exception as e:
        print(f"Error during publishing: {e}")
        return

# Запуск событийного цикла
if __name__ == "__main__":
    asyncio.run(main())

# import asyncio
# from agents.collector import CollectorAgent  
# from agents.manager import ManagerAgent  
# from agents.writer import WriterAgent
# from agents.publisher import PublisherAgent
# from typing import List
# from data_models import NewsItem, NewsDigest

# # Конфигурация RSS-источников
# RSS_SOURCES = [
#     {"region": "World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "days_ago": 0},
#     {"region": "Asia", "url": "https://feeds.bbci.co.uk/news/world/asia/rss.xml", "days_ago": 0},
#     # {"region": "World", "url": "https://www.theguardian.com/world/rss", "days_ago": 0},
#     # {"region": "World", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "days_ago": 0},
# ]

# async def main():
#     # Создание агентов
#     print("Создаём агентов для сбора новостей...")
#     collector_agents = [
#         CollectorAgent(region=source["region"], source_urls=[source["url"]], days_ago=source["days_ago"])
#         for source in RSS_SOURCES
#     ]
#     manager_agent = ManagerAgent()
#     writer_agent = WriterAgent()
#     publisher_agent = PublisherAgent()
#     print("Агенты успешно созданы.")

#     # Сбор новостей
#     all_news = []
#     try:
#         print("Начинаем сбор новостей...")
#         for collector in collector_agents:
#             news: List[NewsItem] = await collector.process()
#             all_news.extend(news)
#             print(f"Собрано {len(news)} новостей для региона {collector.region}.")
#     except Exception as e:
#         print(f"Error during news collection: {e}")
#         return

#     print(f"Всего собрано {len(all_news)} новостей.")

#     # Обработка новостей менеджером
#     try:
#         print("Передача новостей в ManagerAgent для анализа...")
#         filtered_news: List[NewsItem] = await manager_agent.process(all_news)
#         print("Анализ новостей завершен.")
#     except Exception as e:
#         print(f"Error during news filtering and analysis: {e}")
#         return

#     # Генерация итогового дайджеста
#     try:
#         print("Передача новостей в WriterAgent для создания дайджеста...")
#         digest: NewsDigest = await writer_agent.process(filtered_news)
#         print("Дайджест успешно создан.")

#         # Вывод итогового дайджеста
#         print("Generated Digest:")
#         print(f"Date Generated: {digest.date_generated}")
#         print(f"Region: {digest.region}")
#         print("Summary:")
#         print(digest.summary)
#     except Exception as e:
#         print(f"Error during digest generation: {e}")
#         return

#     # Публикация в Telegram
#     try:
#         print("Публикация дайджеста в Telegram...")
#         await publisher_agent.process(digest)  # Отправляем дайджест через PublisherAgent
#         print("Дайджест успешно опубликован в Telegram.")
#     except Exception as e:
#         print(f"Error during publishing: {e}")
#         return

# if __name__ == "__main__":
#     asyncio.run(main())
