import re
from uuid import UUID
from sqlalchemy import select
from transformers import pipeline
from app.models.buzz_monitor import Post

# Constants
MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
SENTIMENT_ANALYSIS = "sentiment-analysis"

# Takes a topic & runs sentiment analysis on all associated posts
def sentiment_analysis(topic_id, db_session):
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
        select(Post).where(Post.topic_id == topic_id)
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
    return content[:512].strip()

# Call the huggingface sentiment analysis pipeline & update posts
def run_sentiment_analysis(content: str, post: Post, pipeline):
    sentiment = pipeline(content)
    post.sentiment_label = sentiment[0]["label"]
    post.sentiment_score = sentiment[0]["score"]
