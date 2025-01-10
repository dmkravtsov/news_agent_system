from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import List, Optional

class NewsItem(BaseModel):
    source: str = Field(..., min_length=1, description="The source of the news item")
    title: str = Field(..., min_length=1, description="The title of the news item")
    description: str = Field(..., description="A short description of the news item")
    date: datetime = Field(..., description="The publication date of the news item")
    region: str = Field(..., description="The region associated with the news item")
    url: HttpUrl = Field(..., description="The URL of the news item source")
    tags: Optional[List[str]] = Field(default_factory=list, description="A list of tags for the news item")
    category: Optional[str] = Field(None, description="The category of the news item (e.g., AI, ML, Stats)")
    language: Optional[str] = Field(None, description="The language of the news item")
    sentiment: Optional[float] = Field(0.0, ge=-1.0, le=1.0, description="The sentiment score of the news item (-1.0 to 1.0)")


class NewsDigest(BaseModel):
    date_generated: datetime = Field(..., description="The date and time the digest was generated")
    items: List[NewsItem] = Field(..., description="A list of news items included in the digest")
    summary: str = Field(..., description="A summary of the news digest")
    region: Optional[str] = Field(None, description="The region of the news digest, if applicable")

