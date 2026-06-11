from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime

## Topics
class TopicBase(BaseModel):
    title: str
    description: str
    is_active: bool
    project_id: UUID

class TopicResponse(TopicBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class TopicUpdate(TopicBase):
    title: Optional[str] = None
    description: Optional[str] = None

## Keywords
class KeywordBase(BaseModel):
    topic_id: UUID
    project_id: UUID
    keyword: str

class KeywordResponse(KeywordBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

## Platforms
class PlatformBase(BaseModel):
    name: str

class PlatformResponse(PlatformBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

## Projects_Platforms
class ProjectPlatformBase(BaseModel):
    project_id: UUID
    platform_id: UUID

## Posts
class PostBase(BaseModel):
    topic_id: UUID
    project_id: UUID
    platform_id: UUID
    original_poster: str
    posted_time: datetime
    content_type: Literal['post', 'comment', 'video']
    content: str

class PostResponse(PostBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class PostCountsUpdate(PostBase):
    view_count: Optional[int]
    like_count: Optional[int]
    comment_count: Optional[int]

class PostCountsResponse(PostBase):
    view_count: Optional[int]
    like_count: Optional[int]
    comment_count: Optional[int]
    model_config = ConfigDict(from_attributes=True)

class PostSentimentUpdate(PostBase):
    sentiment_label: Optional[Literal['positive', 'negative', 'neutral']]
    sentiment_score: Optional[float]

class PostSentimentResponse(PostBase):
    id: UUID
    sentiment_label: Optional[Literal['positive', 'negative', 'neutral']]
    sentiment_score: Optional[float]
    model_config = ConfigDict(from_attributes=True)