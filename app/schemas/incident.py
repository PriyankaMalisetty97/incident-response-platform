from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from app.models.incident import Severity, Status

# Trims spaces, then requires at least 1 character, so "   " is rejected.
Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Service = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class IncidentCreate(BaseModel):
    """What a client must send to create an incident."""

    title: Title
    description: Text
    service: Service
    severity: Severity
    error_message: str | None = None


class IncidentUpdate(BaseModel):
    """PATCH body: every field optional, only the ones sent are changed."""

    title: Title | None = None
    description: Text | None = None
    service: Service | None = None
    severity: Severity | None = None
    status: Status | None = None
    error_message: str | None = None

    @model_validator(mode="after")
    def no_null_for_required_fields(self):
        # Leaving a field out is fine. Sending it as null would blank a required column.
        for name in self.model_fields_set - {"error_message"}:
            if getattr(self, name) is None:
                raise ValueError(f"'{name}' cannot be null")
        return self


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
