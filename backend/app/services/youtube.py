import os
from dotenv import load_dotenv
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from app.models.buzz_monitor import Post

# Load env variables
load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Other constants
MAX_RESULTS = 10

# Return youtube service object using discovery.build function
def get_youtube_client():
    youtube = discovery.build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    return youtube

# Search videos associated with the keywords & return their IDs
def search_videos(keywords: list[str], max_results: int = MAX_RESULTS):
    youtube = get_youtube_client()
    id_list = list()
    # For each keyword, send a request & retrieve data
    for keyword in keywords:
        request = youtube.search().list(
            part="id",
            q=keyword,
            type="video",
            maxResults=max_results
        )
        response = request.execute()
        new_ids = [item['id']['videoId'] for item in response.get('items', [])]
        id_list = id_list + new_ids
    return id_list

# Return metadata from the given list of video IDs
def get_video_metadata(video_ids: list[str]):
    youtube = get_youtube_client() # get youtube service object
    metadata = list()
    # Configure & send request for specified video IDs
    request = youtube.videos().list(
        part="snippet,statistics",
        id=",".join(video_ids)
    )
    response = request.execute()
    # Create a dictionary for each response & append to result
    for data in response['items']:
        new_metadata = dict(
            original_poster=data["snippet"]["channelId"],
            posted_time=data["snippet"]["publishedAt"],
            content_type="video",
            content=data["snippet"]["title"] + "\n\n" + data["snippet"]["description"],
            view_count=data["statistics"]["viewCount"],
            like_count=data["statistics"]["likeCount"],
            comment_count=data["statistics"]["commentCount"]
        )
        metadata.append(new_metadata)
    return metadata

# Fetch comments for a single video
def get_video_comments(video_id: str, max_results: int = MAX_RESULTS):
    youtube = get_youtube_client() # get youtube service object
    metadata = list()
    # Configure & send request for specified video IDs
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=max_results,
        textFormat="plainText"
    )
    response = request.execute()
    # Create a dictionary for each response & append to result
    for data in response['items']:
        comment = data["snippet"]["toplevelComment"]
        new_metadata = dict(
            original_poster=comment["snippet"]["authorDisplayName"],
            posted_time=comment["snippet"]["publishedAt"],
            content_type="comment",
            content=comment["snippet"]["textDisplay"],
            view_count=None,
            like_count=comment["snippet"]["likeCount"],
            comment_count=None
        )
        metadata.append(new_metadata)
    return metadata

# Ingest youtube data -- the whole process
def ingest_youtube_data(topic_id, project_id, platform_id, keywords, db_session):
    # search videos
    video_ids = search_videos(keywords)
    # get metadata & comments
    metadata = get_video_metadata(video_ids)
    comments = list()
    for id in video_ids:
        try:
            new_comments = get_video_comments(id)
            comments += new_comments
        except HttpError:
            continue # Skip videos without comments
    # add data to the database
    # Add post metadata
    for post in metadata:
        new_post = Post(
            topic_id = topic_id,
            project_id = project_id,
            platform_id = platform_id,
            original_poster = post["original_poster"],
            posted_time = post["posted_time"],
            content_type = post["content_type"],
            content = post["content"],
            view_count = post["view_count"],
            like_count = post["like_count"],
            comment_count = post["comment_count"]
        )
        db_session.add(new_post)
    # Add comments
    for comment in comments:
        new_comment = Post(
            topic_id = topic_id,
            project_id = project_id,
            platform_id = platform_id,
            original_poster = comment["original_poster"],
            posted_time = comment["posted_time"],
            content_type = comment["content_type"],
            content = comment["content"],
            view_count = comment["view_count"],
            like_count = comment["like_count"],
            comment_count = comment["comment_count"]
        )
        db_session.add(new_comment)
    db_session.commit()
