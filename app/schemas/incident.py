from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.incident import Severity, Status


class IncidentCreate(BaseModel):
    """What a client must send to create an incident."""

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    service: str = Field(min_length=1, max_length=100)
    severity: Severity
    error_message: str | None = None


class IncidentUpdate(BaseModel):
    """PATCH body: every field optional, only the ones sent are changed."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1)
    service: str | None = Field(default=None, min_length=1, max_length=100)
    severity: Severity | None = None
    status: Status | None = None
    error_message: str | None = None


class IncidentRead(BaseModel):
    """What the API returns. Never expose raw DB objects directly."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    service: str
    severity: Severity
    status: Status
    error_message: str | None
    user_id: int | None
    created_at: datetime
    updated_at: datetime
