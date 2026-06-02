from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime

## Experiments
class Experiment(BaseModel):
    project_id: UUID
    title: str
    description: str
    curr_status: Literal['created', 'running', 'complete', 'archived']
    traffic_split: int
    success_metric: str
    start_time: datetime
    end_time: Optional[datetime]

class ExperimentResponse(Experiment):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

## Assignments
class Assignment(BaseModel):
    session_id: str
    experiment_id: UUID
    variant: Literal['control', 'treatment']

class AssignmentResponse(Assignment):
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

## Events
class Event(BaseModel):
    session_id: str
    experiment_id: UUID
    happened_at: datetime
    event_type: str

class EventResponse(Event):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

## Results
class Result(BaseModel):
    experiment_id: UUID
    control_conversions: Optional[int]
    treatment_conversions: Optional[int]
    control_rate: Optional[float]
    treatment_rate: Optional[float]
    lift: Optional[float]
    confidence: Optional[float]
    winner: Optional[str]

class ResultResponse(Result):
    model_config = ConfigDict(from_attributes=True)