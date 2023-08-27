from pydantic import BaseSettings


class Settings(BaseSettings):
    debug: bool
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_pass: str
    base_url: str

    @property
    def db_uri(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()
