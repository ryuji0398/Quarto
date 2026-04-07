from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # JSON配列形式で渡す: ["https://example.com","https://www.example.com"]
    allowed_origins: list[str] = ["http://localhost:3000", "http://frontend:3000"]
    environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings()
