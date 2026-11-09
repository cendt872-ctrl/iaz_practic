from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "ІАС Геопросторового Моніторингу ЗСУ (Демо)"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    POSTGRES_USER: str = "uaf_admin"
    POSTGRES_PASSWORD: str = "uaf_secure_pass_2026"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "geo_analytics"
    CORS_ORIGINS: str = "*"

    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
