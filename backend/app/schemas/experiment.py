from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime

## Experiments
class ExperimentBase(BaseModel):
    project_id: UUID
    title: str
    description: str
    traffic_split: int
    success_metric: str

class ExperimentResponse(ExperimentBase):
    id: UUID
    curr_status: Literal['created', 'running', 'complete', 'archived']
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)

class ExperimentUpdate(ExperimentBase):
    title: Optional[str] = None
    description: Optional[str] = None
    traffic_split: Optional[int] = None
    success_metric: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

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

class EventCreate(BaseModel):
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