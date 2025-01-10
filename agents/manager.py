from typing import List
from base_agent import BaseAgent
from data_models import NewsItem
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic import PrivateAttr
import os
import csv
import datetime

class ManagerAgent(BaseAgent):
    """
    Агент-менеджер для обработки новостей.
    Использует LLM для анализа, объединения и структурирования новостей.
    """
    _agent: Agent = PrivateAttr()

    def __init__(self):
        super().__init__(name="ManagerAgent")
        self._agent = Agent(
            model=OpenAIModel(
                "gpt-3.5-turbo",  # Или "gpt-4o"
                api_key=os.getenv("OPENAI_API_KEY")
            ),
            result_type=List[NewsItem],
            system_prompt=(
                "You are a news aggregator and analyzer tasked with processing a corpus of raw news articles. "
                "Your job is to deduplicate, merge related news items, and generate a structured list of concise and meaningful news summaries. "
                "Each news item must include: source, title, description, date, region, URL (if available), tags, category, language, and sentiment. "
                "When merging, combine news items about the same geographical locations, people, or events. "
                "Simplify overly complex descriptions while retaining the essential meaning. "
                "Always return the result as a JSON list of NewsItem objects."
            )
        )

    async def process(self, raw_news: List[NewsItem]) -> List[NewsItem]:
        """
        Обрабатывает новости с помощью LLM.

        :param raw_news: Список объектов NewsItem.
        :return: Список структурированных объектов NewsItem.
        """
        if not raw_news:
            raise ValueError("No news provided for processing.")

        # Преобразуем объекты NewsItem в строки для обработки
        raw_corpus = "\n\n".join(
            f"Source: {news.source}, Title: {news.title}, Description: {news.description}"
            for news in raw_news
        )

        # Передаём корпус текстов в модель
        response = self._agent.run_sync(user_prompt=raw_corpus)

        if not response.data:
            raise ValueError("Failed to generate structured news items.")

        # Записываем новости в CSV-файл
        self._save_to_csv(response.data)

        return response.data

    def _save_to_csv(self, news_list: List[NewsItem]):
        """
        Сохраняет новости в CSV-файл с минимальным форматированием.

        :param news_list: Список объектов NewsItem.
        """
        file_name = "news_archive.csv"
        file_exists = os.path.isfile(file_name)

        with open(file_name, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, quoting=csv.QUOTE_NONE, escapechar='\\')

            # Пишем заголовки, если файл создаётся впервые
            if not file_exists:
                writer.writerow(["Date Generated", "News Item"])

            # Добавляем строки с датой и текстом новости
            for news in news_list:
                writer.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"{news.title}: {news.description}"])
