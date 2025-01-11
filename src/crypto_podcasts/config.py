

from pydantic_settings import BaseSettings, SettingsConfigDict
import typing as t

class DBConfig(BaseSettings):
    COSMOS_URI: t.Optional[str] = None
    COSMOS_DB_ACCOUNT_KEY: t.Optional[str] = None
    COSMOS_DB_NAME: t.Optional[str] = None
    COSMOS_CONTAINER_NAME: t.Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

class WhisperConfig(BaseSettings):

    WHISPER_AZURE_API_KEY : t.Optional[str] = None
    WHISPER_API_VERSION : t.Optional[str] = None
    WHISPER_DEPLOYMENT_ID : t.Optional[str] = None
    WHISPER_API_ENDPOINT:t.Optional[str] = None