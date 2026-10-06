from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.incident import Severity, Status
from app.schemas.incident import IncidentCreate, IncidentRead, IncidentUpdate
from app.services import incident_service

router = APIRouter(prefix="/incidents", tags=["incidents"])


def _get_or_404(db: Session, incident_id: int):
    incident = incident_service.get_incident(db, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return incident


@router.post("", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
def create_incident(data: IncidentCreate, db: Session = Depends(get_db)):
    return incident_service.create_incident(db, data)


@router.get("", response_model=list[IncidentRead])
def list_incidents(
    severity: Severity | None = None,
    status: Status | None = None,
    service: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return incident_service.list_incidents(
        db, severity=severity, status=status, service=service, limit=limit, offset=offset
    )


@router.get("/{incident_id}", response_model=IncidentRead)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, incident_id)


@router.patch("/{incident_id}", response_model=IncidentRead)
def update_incident(incident_id: int, data: IncidentUpdate, db: Session = Depends(get_db)):
    incident = _get_or_404(db, incident_id)
    return incident_service.update_incident(db, incident, data)


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = _get_or_404(db, incident_id)
    incident_service.delete_incident(db, incident)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
