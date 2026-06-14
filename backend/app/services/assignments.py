import hashlib
from uuid import UUID
from app.constants import CONTROL, TREATMENT

# Return a new variant using MD5 with built-in hashlib
def get_variant(session_id: str, experiment_id: str, traffic_split: int):
    # Create a unique identifier string combining two IDs
    identifier = f"{session_id}{experiment_id}"
    # Generate MD5 hash
    hash = hashlib.md5(identifier.encode('utf-8'))
    # Convert hash to hexadecimal string then to integer
    hash_int = int(hash.hexdigest(), 16) # 16 specifies which base (hex)
    # Normalize to a value between 0 and 1
    normalized = (hash_int % 100) / 100.0
    # Assign group based on the split threshold & return 
    if normalized < traffic_split:
        return CONTROL
    else:
        return TREATMENT