from keybert import KeyBERT
from pydantic_ai import Agent, RunContext
from typing import List
from data_models import NewsItem
from langdetect import detect
from textblob import TextBlob
import nltk

# Загрузка необходимых пакетов NLTK
nltk.download('stopwords')
nltk.download('punkt')

class ManagerAgent(Agent[List[NewsItem], List[NewsItem]]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keybert_model = KeyBERT()

    async def filter_and_analyze(self, ctx: RunContext[List[NewsItem]]) -> List[NewsItem]:
        # print("Inside filter_and_analyze method...")
        # print(f"Context: {ctx}")
        try:
            result = await self.tool_remove_duplicates(ctx)
            result = await self.tool_semantic_filter(ctx, result)
            result = await self.tool_fill_missing_attributes(ctx, result)
            return result
        except Exception as e:
            print(f"Error in filter_and_analyze: {e}")
            raise e

    async def tool_remove_duplicates(self, ctx: RunContext[List[NewsItem]]) -> List[NewsItem]:
        news_list = ctx.messages
        print(f"Removing duplicates from {len(news_list)} items...")
        unique_titles = set()
        filtered = []
        for item in news_list:
            if item.title not in unique_titles:
                unique_titles.add(item.title)
                filtered.append(item)
        print(f"Removed duplicates, {len(filtered)} items remain.")
        return filtered

    async def tool_semantic_filter(self, ctx: RunContext[List[NewsItem]], news_list: List[NewsItem]) -> List[NewsItem]:
        print("Starting semantic filtering...")
        # Semantic filtering логика может быть упрощена или удалена, если не нужна
        return news_list

    async def tool_fill_missing_attributes(self, ctx: RunContext[List[NewsItem]], news_list: List[NewsItem]) -> List[NewsItem]:
        print("Filling missing attributes...")
        for item in news_list:
            if item.category is None:
                title_lower = item.title.lower()
                description_lower = item.description.lower()
                if any(word in title_lower or description_lower for word in ["politics", "government", "election", "policy", "diplomacy"]):
                    item.category = "Politics"
                elif any(word in title_lower or description_lower for word in ["economy", "finance", "stock", "market", "business"]):
                    item.category = "Economy"
                elif any(word in title_lower or description_lower for word in ["weather", "climate", "storm", "rain", "forecast"]):
                    item.category = "Weather"
                elif any(word in title_lower or description_lower for word in ["sports", "football", "basketball", "tennis", "olympics"]):
                    item.category = "Sports"
                elif any(word in title_lower or description_lower for word in ["health", "medicine", "doctor", "hospital", "disease", "wellness"]):
                    item.category = "Health"
                else:
                    item.category = "General"

            if item.language is None:
                try:
                    item.language = detect(item.title)
                except:
                    item.language = "unknown"

            if item.sentiment is None:
                sentiment = TextBlob(item.description).sentiment.polarity
                item.sentiment = round(sentiment, 2)

            if item.tags is None:
                text = f"{item.title} {item.description}"
                keywords = self.keybert_model.extract_keywords(
                    text,
                    keyphrase_ngram_range=(1, 2),
                    stop_words='english',
                    top_n=5,
                    use_maxsum=True,
                    diversity=0.7
                )


                # Фильтруем слишком общие слова и фразы
                item.tags = [
                    kw[0] for kw in keywords if len(kw[0].split()) <= 2 and kw[0].lower() not in ['people', 'help', 'conditions']
                ]


        print("Attributes filling completed.")
        return news_list

