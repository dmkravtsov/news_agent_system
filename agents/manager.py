from base_agent import BaseAgent
from typing import List
from data_models import NewsItem
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from keybert import KeyBERT
from langdetect import detect
from textblob import TextBlob

class ManagerAgent(BaseAgent):
    """
    Агент-менеджер для обработки новостей.
    Выполняет задачи: удаление дубликатов, объединение схожих новостей,
    определение тональности и заполнение отсутствующих атрибутов.
    """

    def __init__(self):
        super().__init__(name="ManagerAgent")
        self.keybert_model = KeyBERT()  # Модель для извлечения ключевых слов
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Модель для генерации эмбеддингов

    async def process(self, data: List[NewsItem]) -> List[NewsItem]:
        """
        Основной метод обработки данных.

        :param data: Список новостей для обработки.
        :return: Обработанный список новостей.
        """
        await self.log("Starting news processing...")

        # Удаление дубликатов
        data = await self.remove_duplicates(data)

        # Семантическое объединение схожих новостей
        data = await self.semantic_filter(data)

        # Заполнение отсутствующих атрибутов
        data = await self.fill_missing_attributes(data)

        await self.log("News processing completed.")
        return data

    async def remove_duplicates(self, news_list: List[NewsItem]) -> List[NewsItem]:
        """
        Удаляет дубликаты новостей на основе заголовков.

        :param news_list: Список новостей.
        :return: Список новостей без дубликатов.
        """
        unique_titles = set()
        filtered = []
        for item in news_list:
            if item.title not in unique_titles:
                unique_titles.add(item.title)
                filtered.append(item)
        await self.log(f"Removed duplicates: {len(news_list) - len(filtered)} duplicates found.")
        return filtered

    async def semantic_filter(self, news_list: List[NewsItem]) -> List[NewsItem]:
        """
        Объединяет схожие по смыслу новости в группы.

        :param news_list: Список новостей.
        :return: Обработанный список новостей.
        """
        if not news_list:
            return []

        # Создание эмбеддингов для текстов
        texts = [f"{item.title} {item.description}" for item in news_list]
        embeddings = self.embedding_model.encode(texts)

        # Матрица сходства
        similarity_matrix = cosine_similarity(embeddings)
        threshold = 0.3  # Порог сходства
        grouped_indices = set()
        grouped_news = []

        for i, row in enumerate(similarity_matrix):
            if i in grouped_indices:
                continue

            group = [i]
            for j, similarity in enumerate(row):
                if i != j and similarity >= threshold and j not in grouped_indices:
                    group.append(j)

            grouped_indices.update(group)

            # Объединение новостей в группу
            merged_title = "; ".join(news_list[idx].title for idx in group)
            merged_description = " ".join(news_list[idx].description for idx in group)

            grouped_news.append(NewsItem(
                source=news_list[group[0]].source,
                title=merged_title,
                description=merged_description,
                full_text=news_list[group[0]].full_text,
                date=news_list[group[0]].date,
                region=news_list[group[0]].region,
                url=news_list[group[0]].url,
                tags=news_list[group[0]].tags,
                category=news_list[group[0]].category,
                language=news_list[group[0]].language,
                sentiment=news_list[group[0]].sentiment
            ))

        await self.log(f"Semantic filtering completed. Reduced to {len(grouped_news)} items.")
        return grouped_news

    async def fill_missing_attributes(self, news_list: List[NewsItem]) -> List[NewsItem]:
        """
        Заполняет отсутствующие атрибуты для каждой новости.

        :param news_list: Список новостей.
        :return: Список новостей с заполненными атрибутами.
        """
        for item in news_list:
            # Определение категории
            if not item.category:
                title_lower = item.title.lower()
                description_lower = item.description.lower()
                if any(word in title_lower or description_lower for word in ["politics", "government", "election"]):
                    item.category = "Politics"
                elif any(word in title_lower or description_lower for word in ["economy", "finance", "market"]):
                    item.category = "Economy"
                else:
                    item.category = "General"

            # Определение языка
            if not item.language:
                try:
                    item.language = detect(item.title)
                except Exception:
                    item.language = "unknown"

            # Определение тональности
            if not item.sentiment:
                item.sentiment = round(TextBlob(item.description).sentiment.polarity, 2)

            # Извлечение ключевых слов
            if not item.tags:
                text = f"{item.title} {item.description}"
                keywords = self.keybert_model.extract_keywords(
                    text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=5
                )
                item.tags = [kw[0] for kw in keywords]

        await self.log("Attributes filling completed.")
        return news_list

