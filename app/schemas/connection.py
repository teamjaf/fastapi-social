from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from app.schemas.profile import ProfilePublic


class ConnectionStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    BLOCKED = "blocked"


class ConnectionBase(BaseModel):
    status: ConnectionStatus = ConnectionStatus.PENDING


class ConnectionCreate(ConnectionBase):
    addressee_id: int

    @validator('addressee_id')
    def validate_addressee_id(cls, v):
        if v <= 0:
            raise ValueError('Addressee ID must be positive')
        return v


class ConnectionUpdate(BaseModel):
    status: ConnectionStatus
    responded_at: Optional[datetime] = None


class ConnectionResponse(BaseModel):
    id: int
    requester: ProfilePublic
    addressee: ProfilePublic
    status: ConnectionStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConnectionStatusResponse(BaseModel):
    user_id: int
    status: Optional[ConnectionStatus] = None
    connection_id: Optional[int] = None
    connected_since: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConnectionStatsResponse(BaseModel):
    total_connections: int
    pending_received: int
    pending_sent: int
    blocked_users: int

    class Config:
        from_attributes = True


class ConnectionSuggestion(BaseModel):
    user: ProfilePublic
    mutual_connections_count: int
    common_university: bool
    common_major: bool
    common_interests: List[str]
    suggestion_score: float

    class Config:
        from_attributes = True


class ConnectionListResponse(BaseModel):
    connections: List[ConnectionResponse]
    total: int
    limit: int
    offset: int

    class Config:
        from_attributes = True


class ConnectionSuggestionListResponse(BaseModel):
    suggestions: List[ConnectionSuggestion]
    total: int
    limit: int
    offset: int

    class Config:
        from_attributes = True


class MutualConnectionResponse(BaseModel):
    mutual_connections: List[ProfilePublic]
    total: int
    limit: int
    offset: int

    class Config:
        from_attributes = True
