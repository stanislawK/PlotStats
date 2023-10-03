from loguru import logger
from pydantic import BaseSettings

logger.add("file_{time:YYYY-MM-DD}.log", rotation="50 MB", retention="10 days")


class Settings(BaseSettings):
    debug: bool
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_pass: str
    base_url: str
    celery_broker_url: str
    celery_result_backend: str
    redbeat_redis_url: str
    imports: tuple[str] = ("api.periodic_tasks",)

    @property
    def db_uri(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()
