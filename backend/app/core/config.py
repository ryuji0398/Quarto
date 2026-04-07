import json
import os
from dataclasses import dataclass, field


def _parse_origins(raw: str) -> list[str]:
    """
    環境変数 ALLOWED_ORIGINS を list[str] に変換する。
    JSON配列形式: '["https://a.com","https://b.com"]'
    カンマ区切り形式: 'https://a.com,https://b.com'
    空文字列: デフォルト値を使用
    """
    raw = raw.strip()
    if not raw:
        return ["http://localhost:3000", "http://frontend:3000"]
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [str(o) for o in parsed]
    except (json.JSONDecodeError, ValueError):
        pass
    return [o.strip() for o in raw.split(",") if o.strip()]


@dataclass
class Settings:
    allowed_origins: list[str] = field(default_factory=list)
    environment: str = "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings(
    allowed_origins=_parse_origins(os.environ.get("ALLOWED_ORIGINS", "")),
    environment=os.environ.get("ENVIRONMENT", "development"),
)
