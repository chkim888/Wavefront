from uuid import UUID
from sqlalchemy import select
from app.models.buzz_monitor import Post

# Takes a topic & runs sentiment analysis on all associated posts
def sentiment_analysis(topic_id, db_session):
    # fetch relevant posts from database
    post_ids = fetch_posts(topic_id, db_session)
    # For each post
    for id in post_ids:
        # clean up the data 
        clean_post_data(id, db_session)
        # call the huggingface pipeline & store results
        run_sentiment_analysis(id, db_session)

# Fetch all posts (ID only) from database associated with the input topic ID
def fetch_posts(topic_id: UUID, db_session):
    post_ids = db_session.scalars(
        select(Post.id).where(Post.topic_id == topic_id)
    ).all()
    return post_ids

# Clean up post content data
def clean_post_data(post_id: UUID, db_session):
    pass

# Call the huggingface sentiment analysis pipeline & update posts
def run_sentiment_analysis(post_id: UUID, db_session):
    pass