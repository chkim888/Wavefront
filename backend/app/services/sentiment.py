import re
from uuid import UUID
from sqlalchemy import select, and_
from app.models.buzz_monitor import Post
from app.constants import SENTIMENT_ANALYSIS

try:
    from transformers import pipeline
    from app.constants import MODEL
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Takes a topic & runs sentiment analysis on all associated posts
def sentiment_analysis(topic_id, db_session):
    if not TRANSFORMERS_AVAILABLE:
        print("Transformers not available; skipping sentiment analysis")
        return
    # fetch relevant posts from database
    posts = fetch_posts(topic_id, db_session)
    # Initialize the huggingface pipeline
    pipe = pipeline(SENTIMENT_ANALYSIS, model=MODEL, tokenizer=MODEL)
    # For each post
    for post in posts:
        # clean up the data (basic parsing)
        cleaned_content = clean_post_data(post.content)
        # call the huggingface pipeline & store results
        run_sentiment_analysis(cleaned_content, post, pipe)
    # Update all changes
    db_session.commit()

# Fetch all posts (ID only) from database associated with the input topic ID
def fetch_posts(topic_id: UUID, db_session):
    posts = db_session.scalars(
        select(Post).where(and_(
            Post.topic_id == topic_id,
            Post.sentiment_label.is_(None)
        ))
    ).all()
    return posts

# Clean up post content data
def clean_post_data(content: str):
    content = re.sub(r'http\S+', '', content)   # strip URLs
    content = re.sub(r'@\w+', '', content)      # strip mentions
    content = re.sub(r'#\w+', '', content)      # strip hashtags
    content = re.sub(r'\n+', ' ', content)      # collapse newlines
    content = re.sub(r' +', ' ', content)       # collapse spaces
    content = content.lower()                   # lowercase
    return content

# Call the huggingface sentiment analysis pipeline & update posts
def run_sentiment_analysis(content: str, post: Post, pipeline):
    try:
        sentiment = pipeline(content, truncation=True, max_length=512)
        post.sentiment_label = sentiment[0]["label"]
        post.sentiment_score = sentiment[0]["score"]
    except Exception as e:
        print(f"Skipping post {post.id}: {e}")
