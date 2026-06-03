from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime

## Experiments
class ExperimentBase(BaseModel):
    project_id: UUID
    title: str
    description: str
    curr_status: Literal['created', 'running', 'complete', 'archived']
    traffic_split: int
    success_metric: str
    start_time: datetime
    end_time: Optional[datetime]

class ExperimentResponse(ExperimentBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

## Assignments
class AssignmentBase(BaseModel):
    session_id: str
    experiment_id: UUID
    variant: Literal['control', 'treatment']

class AssignmentResponse(AssignmentBase):
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

## Events
class EventBase(BaseModel):
    session_id: str
    experiment_id: UUID
    happened_at: datetime
    event_type: str

class EventResponse(EventBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

## Results
class ResultBase(BaseModel):
    experiment_id: UUID
    control_conversions: Optional[int]
    treatment_conversions: Optional[int]
    control_rate: Optional[float]
    treatment_rate: Optional[float]
    lift: Optional[float]
    confidence: Optional[float]
    winner: Optional[str]

class ResultResponse(ResultBase):
    model_config = ConfigDict(from_attributes=True)