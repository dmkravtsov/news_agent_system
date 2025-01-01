import asyncio
from agents.collector import CollectorAgent  
from agents.manager import ManagerAgent  
from agents.writer import WriterAgent
from agents.publisher import PublisherAgent
from typing import List
from data_models import NewsItem, NewsDigest

# Списки RSS-источников для разных регионов
RSS_URL_WORLD = "https://feeds.bbci.co.uk/news/world/rss.xml"
RSS_URL_ASIA = "https://feeds.bbci.co.uk/news/world/asia/rss.xml"
RSS_URL_ARXIV = 'https://arxiv.org/rss/cs.AI+cs.LG+stat.ML'


async def main():
    # Создание агентов
    print("Создаём агентов для сбора новостей...")
    collector_world = CollectorAgent(region="World", source_urls=[RSS_URL_WORLD], days_ago=0)
    collector_asia = CollectorAgent(region="Asia", source_urls=[RSS_URL_ASIA],days_ago=0)
    collector_arxiv = CollectorAgent(region="Arxiv", source_urls=[RSS_URL_ARXIV],days_ago=0)
    manager_agent = ManagerAgent()
    writer_agent = WriterAgent()
    publisher_agent = PublisherAgent()  # Новый агент для публикации
    print("Агенты успешно созданы.")

    # Сбор новостей
    try:
        print("Начинаем сбор новостей...")
        news_world: List[NewsItem] = await collector_world.process()
        news_asia: List[NewsItem] = await collector_asia.process()
        news_arxiv: List[NewsItem] = await collector_arxiv.process()

        print(f"Собрано {len(news_world)} новостей для региона World.")
        print(f"Собрано {len(news_asia)} новостей для региона Asia.")
        print(f"Собрано {len(news_arxiv)} новостей для региона Asia.")
    except Exception as e:
        print(f"Error during news collection: {e}")
        return

    # Объединение новостей
    all_news = news_world + news_asia + news_arxiv

    print(f"Всего собрано {len(all_news)} новостей.")

    # Обработка новостей менеджером
    try:
        print("Передача новостей в ManagerAgent для анализа...")
        filtered_news: List[NewsItem] = await manager_agent.process(all_news)
        print("Анализ новостей завершен.")
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

if __name__ == "__main__":
    asyncio.run(main())