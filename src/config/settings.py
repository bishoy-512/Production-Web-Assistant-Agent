from enum import StrEnum
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings,SettingsConfigDict
from pydantic import Field,field_validator,model_validator
from typing import Optional
import os

class Environment(StrEnum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    TEST = "test"
    PRODUCTION = "production"
    
class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class LogRenderer(StrEnum):
    CONSOLE = "console"
    JSON = "json"

def get_environment() -> Environment:
    match os.getenv("APP_ENV", "development").lower():
        case "production" | "prod":
            return Environment.PRODUCTION
        case "staging" | "stage":
            return Environment.STAGING
        case "testing" | "test":
            return Environment.TEST
        case _:
            return Environment.DEVELOPMENT
        

def load_env_file() -> str | Path | None:
    env = get_environment()
    print(f"Loading environment: {env}")
    base_dir = Path(__file__).parents[2]

    # Define env files in priority order
    env_files = [Path(base_dir, f".env.{env.value}"), Path(base_dir, ".env")] 

    # Load the first env file that exists
    for env_file in env_files:
        if env_file.is_file():
            load_dotenv(env_file, override=True)
            print(f"Loaded environment from {env_file}")
            return env_file
        
ENV_FILE = load_env_file()

class Settings(BaseSettings):
    # Project Information
    APP_ENV: Environment = Field(...)
    APP_NAME: str = Field(..., max_length=100)
    VERSION: str = Field(...)
    PROJECT_ROOT: str = Field(...)
    
    # Logging Settings
    DEBUG: Optional[bool] = Field(default=None)
    LOG_LEVEL: Optional[LogLevel] = Field(default=None)
    LOG_RENDER: Optional[LogRenderer] = Field(default=None)
    LOG_DIR: Optional[str] = Field(default="storage/logs")
    LOG_MAX_BYTES: Optional[int] = Field(default=10485760)
    LOG_BACKUP_COUNT: Optional[int] = Field(default=10)
    
    # DataBase Connection
    POSTGRES_HOST: str = Field(...)
    POSTGRES_DB: str = Field(...)
    POSTGRES_USER: str = Field(...)
    POSTGRES_PORT: int = Field(...)
    POSTGRES_PASSWORD: str = Field(...)
    POSTGRES_POOL_SIZE: int = Field(...)
    POSTGRES_MAX_OVERFLOW: int = Field(...)
    
    model_config = SettingsConfigDict(env_file=ENV_FILE)
    
    @field_validator("APP_ENV", mode="before")
    @classmethod
    def normalize_environment(cls, value: str) -> str:
        if isinstance(value, Environment):
            return value

        aliases = {
            "dev": "development",
            "development": "development",
            "stage": "staging",
            "staging": "staging",
            "prod": "production",
            "production": "production",
            "test": "test",
            "testing": "test",
        }

        normalized_env = aliases.get(str(value).lower())
        if normalized_env is None:
            raise ValueError(
                f"Invalid APP_ENV '{value}'."
                f"Expected one of: {', '.join(sorted(aliases.keys()))}"
            )

        return normalized_env
    
def get_settings():
    return Settings()

settings = get_settings()


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )
    for key, value in settings.model_dump().items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()

