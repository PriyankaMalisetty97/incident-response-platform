"""Business logic for incidents. Routes stay thin; all DB work lives here."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.incident import Incident, Severity, Status
from app.schemas.incident import IncidentCreate, IncidentUpdate


def create_incident(db: Session, data: IncidentCreate, user_id: int | None = None) -> Incident:
    incident = Incident(**data.model_dump(), user_id=user_id)
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def get_incident(db: Session, incident_id: int) -> Incident | None:
    return db.get(Incident, incident_id)


def list_incidents(
    db: Session,
    *,
    severity: Severity | None = None,
    status: Status | None = None,
    service: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Incident]:
    query = select(Incident)
    if severity:
        query = query.where(Incident.severity == severity)
    if status:
        query = query.where(Incident.status == status)
    if service:
        query = query.where(Incident.service == service)
    query = query.order_by(Incident.created_at.desc(), Incident.id.desc()).limit(limit).offset(offset)
    return list(db.scalars(query))


def update_incident(db: Session, incident: Incident, data: IncidentUpdate) -> Incident:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(incident, field, value)
    db.commit()
    db.refresh(incident)
    return incident


def delete_incident(db: Session, incident: Incident) -> None:
    db.delete(incident)
    db.commit()
