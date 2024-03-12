import binascii
import logging
import os
import secrets
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field, SecretBytes, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from . import toolbox

logger = logging.getLogger(__name__)


DEFAULT_MODULE_NAME = "app"
BASE_DIR = toolbox.module_to_os_path(DEFAULT_MODULE_NAME)
STATIC_DIR = Path(BASE_DIR) / "static"
TEMPLATE_DIR = Path(BASE_DIR) / "templates"
DATA_DIR = Path(BASE_DIR).parent / "data"
LOG_DIR = Path(BASE_DIR).parent / "_logs"


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True, env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    APP_FACTORY_LOC: str = "app.main:create_app"
    PORT: int = 8000
    LITESTAR_RELOAD: bool = True

    ENV_STATE: str = Field(default="dev", validation_alias="ENV_STATE")

    NAME: str = "Demolite: Checking Out Litestar"
    DESCRIPTION: str = "Testing Litestar with HTMX and Tailwind"
    VERSION: str = "0.1.0"
    STATIC_URL: str = "/static"
    STATIC_DIR: Path = STATIC_DIR
    JWT_SECRET_KEY: SecretBytes | None = None

    ENCODING_SECRET: str = secrets.token_hex(16)

    EXTERNAL_DOCS: dict = {
        "description": "Docs for Demolite",
        "url": "https://github.com/demolite/demolite",
    }

    DISABLE_OPENAPI: bool | None = False

    DATABASE_URI: str | None = Field(default=None, validation_alias="DATABASE_URI")

    POSTGRES_DB_NAME: str | None = None
    POSTGRES_HOST: str | None = None
    POSTGRES_PORT: int | None = None
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None

    DATABASE_CONNECTION_ARGS: dict[str, Any] | None = {"check_same_thread": False}
    DATABASE_ECHO: str | None = None

    ALEMBIC_CONFIG: Path = Path(BASE_DIR).parent / "alembic.ini"
    ALEMBIC_MIGRATION_PATH: Path = Path(BASE_DIR) / "db" / "migrations"
    DATA_DIR: Path = DATA_DIR

    LOG_DIR: Path = LOG_DIR
    LOG_FILENAME: str = "iesl.log"
    LOG_LEVEL: int = logging.INFO
    LOG_FILE_MODE: str = "w"

    @field_validator("JWT_SECRET_KEY", mode="before")
    @classmethod
    def generate_secret_key(cls, value: str | None) -> SecretBytes:
        if value is None:
            return SecretBytes(binascii.hexlify(os.urandom(32)))
        return SecretBytes(value.encode())


class DevConfig(AppConfig):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="DEV_",
        extra="allow",
    )

    DEBUG: bool = True


class TestConfig(AppConfig):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env.testing",
        env_file_encoding="utf-8",
        env_prefix="TEST_",
        extra="allow",
    )


class StgConfig(AppConfig):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="STG_",
        extra="allow",
    )


class PrdConfig(AppConfig):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="PRD_",
        extra="allow",
    )


class FactoryConfig:
    """Inherits configuration from AppConfig. Depending on `ENV_STATE`,
    it will inherit from DevConfig, TestConfig, StgConfig, or PrdConfig.
    For example, the .env values with "DEV_" prefix are loaded when the
    `ENV_STATE` is "dev", and the same for respective `env_prefix` values.
    """

    def __init__(self, env_state: str | None) -> None:
        self.env_state = env_state

    def __call__(self) -> DevConfig | TestConfig | StgConfig | PrdConfig:
        if self.env_state in ("dev", None):
            logger.warning(
                "Environment variable not found defining the app state. "
                "Will default to 'Dev' environment."
            )
            config_model = DevConfig()

        elif self.env_state == "test":
            config_model = TestConfig()  # type: ignore

        elif self.env_state == "stg":
            config_model = StgConfig()  # type: ignore

        elif self.env_state == "prd":
            config_model = PrdConfig()  # type: ignore

            if config_model.DISABLE_OPENAPI:
                config_model.DISABLE_OPENAPI = True
        else:
            raise ValueError(
                f"Unknown ENV_STATE: {self.env_state}. Try updating your .env file."
            )

        self.validate_model_settings(config_model)
        return config_model

    def validate_model_settings(self, model: AppConfig):
        try:
            model.model_validate({})
        except ValidationError as error:
            print(f"Couldn't validate model settings: {error}")
            raise error from error


@lru_cache()
def get_app_settings() -> DevConfig | StgConfig | TestConfig | PrdConfig:
    """Returns a cached instance of the settings (config) object.

    To change env variable and reset cache during testing, use the 'lru_cache'
    instance method 'get_app_settings.cache_clear()'."""

    return FactoryConfig(AppConfig().ENV_STATE)()
