from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Reads configuration from environment variables / the .env file.

    Keeping secrets and connection strings out of the code means the same code
    runs on your laptop, in tests, and later in Docker/AWS.
    """

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/incidents"
    secret_key: str = "change-me-in-production"  # used for JWT in the auth commit
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
