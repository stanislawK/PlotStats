from loguru import logger
from pydantic_settings import BaseSettings

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
    jwt_secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int
    dc1_url: str
    redis_pass: str
    traefik_host: str
    bd_token: str
    unblock_url: str
    imports: tuple[str] = ("api.periodic_tasks",)

    @property
    def db_uri(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()
