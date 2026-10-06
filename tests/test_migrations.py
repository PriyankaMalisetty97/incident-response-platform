"""Guards against forgetting to write a migration after changing a model."""
from alembic import command
from alembic.config import Config


def _config(db_path) -> Config:
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    return cfg


def test_migrations_apply_and_match_models(tmp_path):
    cfg = _config(tmp_path / "migrate.db")
    command.upgrade(cfg, "head")
    # Raises if the models differ from what the migrations build.
    # If this fails: run `alembic revision --autogenerate -m "describe change"`.
    command.check(cfg)


def test_migrations_can_be_reversed(tmp_path):
    cfg = _config(tmp_path / "reverse.db")
    command.upgrade(cfg, "head")
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")
