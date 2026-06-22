# Initializing constants
from urllib.parse import urlparse
import os

# Role
OWNER = "owner"
VIEWER = "viewer"

# Content type
POST = "post"
COMMENT = "comment"
VIDEO = "video"

# Sentiment analysis
POSITIVE = "positive"
NEGATIVE = "negative"
NEUTRAL = "neutral"
MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
SENTIMENT_ANALYSIS = "sentiment-analysis"

# YouTube
MAX_RESULTS = 50

# Spike detection
HOURS = 24

# Experiments
CREATED = "created"
RUNNING = "running"
COMPLETE = "complete"
ARCHIVED = "archived"
CONFIDENCE_THRESHOLD = 95

# Results
INCONCLUSIVE = "inconclusive"
INSUFFICIENT_DATA = "insufficient data"

# Assignments
CONTROL = "control"
TREATMENT = "treatment"

# Redis
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
_parsed_redis = urlparse(REDIS_URL)
REDIS_HOST = _parsed_redis.hostname
REDIS_PORT = _parsed_redis.port or 6379

# Local
LOCAL_FRONTEND_URL = "http://localhost:5173"