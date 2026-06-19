from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from uuid import UUID
from app.auth.dependencies import get_current_user, permission_check
from app.database import get_db_session
from app.schemas.buzz_monitor import TopicBase, TopicResponse, TopicUpdate, KeywordBase, KeywordResponse, PostBase, PostSentimentUpdate, PostSentimentResponse, PostResponse, PlatformResponse, PostCountsUpdate, PostCountsResponse
from app.models.buzz_monitor import Topic, Keyword, Post, Platform
from app.constants import OWNER, VIEWER

# Router initialization
router = APIRouter(prefix="/topics")

## Create
# Create new topic (for a project)
@router.post("", response_model=TopicResponse)
def create_topic(topic: TopicBase, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    if permission_check(user.id, topic.project_id, db_session) == OWNER:
        new_topic = Topic(
            title=topic.title,
            description=topic.description,
            project_id=topic.project_id
        )
        db_session.add(new_topic)
        db_session.commit()
        db_session.refresh(new_topic)
        return new_topic
    
# Create new keyword for a topic (for a topic)
@router.post("/keyword", response_model=KeywordResponse)
def create_keyword(keyword: KeywordBase, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    if permission_check(user.id, keyword.project_id, db_session) == OWNER:
        new_keyword = Keyword(
            topic_id=keyword.topic_id,
            project_id=keyword.project_id,
            keyword=keyword.keyword
        )
        db_session.add(new_keyword)
        db_session.commit()
        db_session.refresh(new_keyword)
        return new_keyword

## Read
# Read the list of available social media platforms
@router.get("/platforms", response_model=list[PlatformResponse])
def get_platforms(db_session=Depends(get_db_session)):
    # Skipping authentication step since public information
    platforms = db_session.scalars(select(Platform)).all()
    if platforms:
        return platforms
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform not found"
        )

# Read list of keywords for a topic
@router.get("/keywords/{topic_id}", response_model=list[KeywordResponse])
def get_keywords(topic_id: UUID, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    project_id = db_session.scalars(select(Topic.project_id).where(Topic.id == topic_id)).first()
    if project_id:
        if permission_check(user.id, project_id, db_session) in [OWNER, VIEWER]:
            keywords = db_session.scalars(
                select(Keyword).where(Keyword.topic_id == topic_id)
            ).all()
            return keywords
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
# Read list of posts for a topic
@router.get("/posts/{topic_id}", response_model=list[PostResponse])
def get_posts_for_topic(topic_id: UUID, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    project_id = db_session.scalars(select(Topic.project_id).where(Topic.id == topic_id)).first()
    if project_id:
        if permission_check(user.id, project_id, db_session) in [OWNER, VIEWER]:
            posts = db_session.scalars(
                select(Post).where(Post.topic_id == topic_id)
            ).all()
            return posts
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
# Read list of topics for a project
@router.get("/{project_id}", response_model=list[TopicResponse])
def get_topics(project_id: UUID, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    if permission_check(user.id, project_id, db_session) in [OWNER, VIEWER]:
        topics = db_session.scalars(
            select(Topic).where(Topic.project_id == project_id)
        ).all()
        return topics

## Update
# Update topic title and/or description
@router.patch("", response_model=TopicResponse)
def update_topic(updates: TopicUpdate, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    if permission_check(user.id, updates.project_id, db_session) == OWNER:
        topic = db_session.scalars(select(Topic).where(Topic.id == updates.id)).first()
        if updates.title:
            # Check if topic already exists with the same name/title
            existing = db_session.scalars(
                select(Topic).where(
                    and_(Topic.title == updates.title,
                         Topic.project_id == updates.project_id))).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Topic title already in use"
                )
            else:
                topic.title = updates.title
        if updates.description: # Can have duplicate descriptions
            topic.description = updates.description
        db_session.commit()
        db_session.refresh(topic)
        return topic

# (updating keyword skipped -- just delete and/or add a new one)

# Update platform information -- not sure if needed (same as create)

# Update post counts
@router.patch("/counts", response_model=PostCountsResponse)
def update_post_counts(counts: PostCountsUpdate, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    post = db_session.scalars(select(Post).where(Post.id == counts.id)).first()
    if post:
        if permission_check(user.id, post.project_id, db_session) == OWNER:
            if counts.view_count:
                post.view_count = counts.view_count
            if counts.like_count:
                post.like_count = counts.like_count
            if counts.comment_count:
                post.comment_count = counts.comment_count
            db_session.commit()
            db_session.refresh(post)
            return post
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

# Update post sentiment label & score
@router.patch("/sentiment", response_model=PostSentimentResponse)
def update_post_sentiment(sentiment: PostSentimentUpdate, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    post = db_session.scalars(select(Post).where(Post.id == sentiment.id)).first()
    if post:
        if permission_check(user.id, post.project_id, db_session) == OWNER:
            if sentiment.sentiment_label:
                post.sentiment_label = sentiment.sentiment_label
            if sentiment.sentiment_score:
                post.sentiment_score = sentiment.sentiment_score
            db_session.commit()
            db_session.refresh(post)
            return post
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

## Delete
# Delete keyword
@router.delete("/keyword/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_keyword(keyword_id: UUID, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    keyword = db_session.scalars(select(Keyword).where(Keyword.id == keyword_id)).first()
    if keyword:
        if permission_check(user.id, keyword.project_id, db_session) == OWNER:
            db_session.delete(keyword)
            db_session.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )

# Delete post
@router.delete("/post/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: UUID, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    post = db_session.scalars(select(Post).where(Post.id == post_id)).first()
    if post:
        if permission_check(user.id, post.project_id, db_session) == OWNER:
            db_session.delete(post)
            db_session.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
# Delete topic
@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic(topic_id: UUID, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    topic = db_session.scalars(select(Topic).where(Topic.id == topic_id)).first()
    if topic:
        if permission_check(user.id, topic.project_id, db_session) == OWNER:
            db_session.delete(topic)
            db_session.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )