import hashlib
from uuid import UUID
from sqlalchemy import select, and_
from datetime import datetime, timezone
from app.models.experiment import Assignment
from app.constants import CONTROL, TREATMENT

# Return a newly-assigned or old variant for session ID
def get_or_assign_variant(session_id, experiment, db_session):
    # see if assignment already exists for the session -- return if exists
    existing = db_session.scalars(
        select(Assignment).where(and_(
            Assignment.session_id == session_id,
            Assignment.experiment_id == experiment.id
    ))).first()
    if existing:
        return existing
    # determine which variant the session is being assigned to
    traffic_split = experiment.traffic_split
    variant = decide_variant(session_id, str(experiment.id), traffic_split)
    # create a new assignment for the session
    new_assignment = Assignment(
        session_id=session_id,
        experiment_id=experiment.id,
        created_at=datetime.now(timezone.utc),
        variant=variant
    )
    # Push new assignment & return
    db_session.add(new_assignment)
    db_session.commit()
    db_session.refresh(new_assignment)
    return new_assignment

# Return a new variant using MD5 with built-in hashlib
def decide_variant(session_id: str, experiment_id: str, traffic_split: int):
    # Create a unique identifier string combining two IDs
    identifier = f"{session_id}{experiment_id}"
    # Generate MD5 hash
    hash = hashlib.md5(identifier.encode('utf-8'))
    # Convert hash to hexadecimal string then to integer
    hash_int = int(hash.hexdigest(), 16) # 16 specifies which base (hex)
    # Normalize to a value between 0 and 1
    normalized = hash_int % 100
    # Assign group based on the split threshold & return 
    if normalized < traffic_split:
        return CONTROL
    else:
        return TREATMENT