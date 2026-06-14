from sqlalchemy import select, func, and_
import statistics
from datetime import datetime, timezone, timedelta
from app.models.buzz_monitor import Post, Alert
from app.constants import HOURS

# Performs spike detection assessment on a given topic
def spike_detection(topic_id: str, project_id: str, db_session) -> bool:
    # Calculate the number of posts in each hour over the last day
    hourly_counts = list()
    for i in range(HOURS):
        start_time = datetime.now(timezone.utc) - timedelta(hours=i+1)
        end_time = datetime.now(timezone.utc) - timedelta(hours=i)
        post_count = db_session.scalars(
            select(func.count()).select_from(Post).where(and_(
                Post.topic_id == topic_id,
                Post.posted_time >= start_time,
                Post.posted_time < end_time
            ))).one()
        hourly_counts.append(post_count)
    # Calculate standard deviation & mean
    if len(hourly_counts) < 2: # for edge cases that would break stdev
        return False
    sd = statistics.stdev(hourly_counts)
    mean = statistics.mean(hourly_counts)
    # Determine whether the last hour exceeds sd
    threshold = mean + 2 * sd
    if hourly_counts[0] > threshold:
        # Add to alerts table if threshold exceeded
        alert = Alert(
            project_id=project_id,
            topic_id=topic_id,
            triggered_at=datetime.now(timezone.utc),
            message=f"Spike detected: {hourly_counts[0]} mentions in the last hour vs {mean:.1f} average"
        )
        db_session.add(alert)
        db_session.commit()
        return True
    else:
        return False