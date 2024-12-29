from typing import List
from datetime import datetime
from data_models import NewsItem, NewsDigest
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
import os
import nltk
import re

from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv(override=True)

class WriterAgent:
    def __init__(self, max_sentences: int = 3):
        self.max_sentences = max_sentences  # Гиперпараметр: количество предложений из описания
        self.agent = Agent(
            model=OpenAIModel(
                "gpt-3.5-turbo",
                api_key=os.getenv("OPENAI_API_KEY")
            ),
            system_prompt=(
                "You are a professional summarizer. "
                "Group similar news items into one by merging their content and summarizing them concisely. "
                "Ensure all key points are included and avoid repetition."
            )
        )

    async def create_digest(self, news_list: List[NewsItem]) -> NewsDigest:
        if not news_list:
            raise ValueError("The news list is empty. Cannot create a digest.")

        # Формируем сообщение для LLM
        user_message = "Please group and summarize the following news items:\n\n"
        for idx, item in enumerate(news_list, start=1):
            # Ограничиваем описание заданным количеством предложений
            description = self._truncate_to_sentences(item.description or "", self.max_sentences)
            user_message += f"{idx}. Title: {item.title}\n   Description: {description}\n\n"

        # Запрашиваем модель
        response = await self.agent.run(user_message)

        # Проверяем ответ
        if not response.data:
            raise ValueError("Failed to generate a digest summary.")

        # Определяем общий регион
        region = (
            news_list[0].region
            if all(item.region == news_list[0].region for item in news_list)
            else None
        )

        # Создаем объект NewsDigest
        digest = NewsDigest(
            date_generated=datetime.now(),
            items=news_list,
            summary=response.data.strip(),
            region=region
        )
        return digest

    def _truncate_to_sentences(self, text: str, max_sentences: int) -> str:
        """
        Ограничивает текст заданным количеством предложений с использованием регулярных выражений.
        :param text: Исходный текст
        :param max_sentences: Максимальное количество предложений
        :return: Ограниченный текст
        """
        # Используем регулярное выражение для поиска предложений
        sentences = re.split(r'(?<=[.!?]) +', text.strip())
        return " ".join(sentences[:max_sentences])
