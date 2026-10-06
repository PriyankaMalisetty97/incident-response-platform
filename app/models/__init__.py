# Importing the models here makes sure SQLAlchemy registers every table on Base.
from app.models.incident import Incident, Severity, Status  # noqa: F401
from app.models.user import User  # noqa: F401
