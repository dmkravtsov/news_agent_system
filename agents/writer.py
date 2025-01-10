from base_agent import BaseAgent
from typing import List
from datetime import datetime
from data_models import NewsItem, NewsDigest
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic import Field, PrivateAttr
import os
import re
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv(override=True)

class WriterAgent(BaseAgent):
    """
    Агент-писатель для создания дайджестов новостей.
    """
    max_sentences: int = Field(default=3, description="Максимальное количество предложений для описания")
    _agent: Agent = PrivateAttr()

    def __init__(self, max_sentences: int = 3):
        super().__init__(name="WriterAgent")
        self.max_sentences = max_sentences
        self._agent = Agent(
            model=OpenAIModel(
                "gpt-3.5-turbo",
                api_key=os.getenv("OPENAI_API_KEY")
            ),
            system_prompt=(
                "You are a professional summarizer. "
                "Give reply in Russian language. "
                "Group similar news items into one by merging their content and summarizing them concisely in 1 sentence. "
                "Ensure all key points are included and avoid repetition. "
                "The summary must be a numbered list where each item starts with a number followed by a period and a single space (e.g., '1. '), without additional line breaks between items."
            )
        )

    async def process(self, news_list: List[NewsItem]) -> NewsDigest:
        """
        Создаёт дайджест новостей на основе списка объектов NewsItem.

        :param news_list: Список новостей.
        :return: Объект NewsDigest.
        """
        if not news_list:
            raise ValueError("The news list is empty. Cannot create a digest.")

        # Формируем сообщение для LLM
        user_message = self._prepare_message(news_list)

        # Запрашиваем модель
        response = await self._agent.run(user_message)

        # Проверяем ответ
        if not response.data:
            raise ValueError("Failed to generate a digest summary.")

        # Определяем общий регион
        region = (
            news_list[0].region
            if all(item.region == news_list[0].region for item in news_list)
            else None
        )

        # Создаём объект NewsDigest
        digest = NewsDigest(
            date_generated=datetime.now(),
            items=news_list,
            summary=response.data.strip(),
            region=region
        )
        return digest

    def _prepare_message(self, news_list: List[NewsItem]) -> str:
        """
        Формирует сообщение для LLM на основе списка новостей.

        :param news_list: Список новостей.
        :return: Сообщение для LLM.
        """
        user_message = "Please group and summarize the following news items:\n\n"
        for idx, item in enumerate(news_list, start=1):
            description = self._truncate_to_sentences(item.description or "", self.max_sentences)
            user_message += f"{idx}. Title: {item.title}\n   Description: {description}\n\n"
        return user_message

    def _truncate_to_sentences(self, text: str, max_sentences: int) -> str:
        """
        Ограничивает текст заданным количеством предложений с использованием регулярных выражений.

        :param text: Исходный текст
        :param max_sentences: Максимальное количество предложений
        :return: Ограниченный текст
        """
        sentences = re.split(r'(?<=[.!?]) +', text.strip())
        return " ".join(sentences[:max_sentences])
