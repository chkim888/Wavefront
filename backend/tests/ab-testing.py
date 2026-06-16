import uuid
import random
from sqlalchemy import select
from fastapi import HTTPException
from app.models.experiment import Experiment
from app.services.assignments import get_or_assign_variant
from app.routers.events import create_event
from app.database import SessionLocal
from app.schemas.experiment import EventCreate
from app.services.stats_engine import run_stats_engine
from app.constants import CONTROL, RUNNING
'''
This is for checking the A/B testing pipeline end to end
Things that I'll need to test in order:
    1) Create an experiment & set the environment for it
    2) Simulate users accessing the page over and over (loop?)
    3) Check that chi-square test works

Separately test that the browser app works for the demo app
'''

# Set values for necessary variables
NUM_SIM = 500
experiment_id = "f3b6a6db-cbe7-4eac-a83d-0a34bdc772bc"

# adjustable values for different chi-square test winners
# ex) there's 35% chance that user assigned control variant will click on the button 
CONTROL_CHANCE = 0.35
TREATMENT_CHANCE = 0.2

# Create DB session
db_session = SessionLocal()
try:
    # Fetch experiment from db
    experiment = db_session.scalars(select(Experiment).where(Experiment.id == experiment_id)).first()

    # Each simulation is a unique session -- insert in necessary data
    for i in range(NUM_SIM):
        # generate a session ID for the mock user
        session_id = str(uuid.uuid4())
        # get variant assignment for session ID
        result = get_or_assign_variant(session_id, experiment, db_session)
        variant = result.variant
        if variant == CONTROL:
            chance = CONTROL_CHANCE
        else:
            chance = TREATMENT_CHANCE
        # For a certain chance, the "user" can trigger the event endpoint (i.e. click a button)
        if random.random() <= chance:
            event_data = EventCreate(event_type="button_click")
            try:
                create_event(uuid.UUID(experiment_id), session_id, event_data, db_session)
            except HTTPException as e:
                print(f"Event skipped: {e.detail}")

    # Run stats engine & get the result
    result = run_stats_engine(experiment_id, db_session)
    print(f"The winner is {result['winner']} with {result['confidence']} confidence")
finally:
    db_session.close()