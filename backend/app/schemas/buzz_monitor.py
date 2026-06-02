from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime

## Topics
class Topic(BaseModel):
    title: str
    description: str
    project_id: UUID

class TopicResponse(Topic):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

## Keywords
class Keyword(BaseModel):
    topic_id: UUID
    keyword: str

class KeywordResponse(Keyword):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

## Platforms
class Platform(BaseModel):
    name: str

class PlatformResponse(Platform):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

## Posts
class Post(BaseModel):
    topic_id: UUID
    platform_id: UUID
    original_poster: str
    posted_time: datetime
    content_type: Literal['post', 'comment', 'video']
    content: str

class PostSentimentUpdate(Post):
    sentiment_label: Optional[Literal['positive', 'negative', 'neutral']]
    sentiment_score: Optional[float]

class PostResponse(Post):
    id: UUID
    sentiment_label: Optional[Literal['positive', 'negative', 'neutral']]
    sentiment_score: Optional[float]
    model_config = ConfigDict(from_attributes=True)