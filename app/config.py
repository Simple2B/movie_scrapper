import os
from typing import List, Union
from pydantic import AnyHttpUrl, BaseSettings, validator
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # FastApi init settings
    DEBUG: bool = os.getenv("DEBUG", "0") == "1"
    APP_NAME: str = "FastAPI_scrapper"
    APP_DESCRIPTION: str = ""
    APP_VERSION: str = "0.1.1"
    OPENAPI_URL: str = "/api/openapi.json"
    DOCS_URL: str = "/api/docs"
    SWAGGER_UI_OAUTH2_REDIRECT_URL: str = "/api/docs/oauth2-redirect"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Working directories
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DRIVERS_DIR: str = r".drivers"

    # Working files
    FILTER_CONFIGS_PATH: str = os.path.join(BASE_DIR, "filter_configs.json")

    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "ERROR")
    JSON_LOGS: bool = os.getenv("JSON_LOGS", "0") == "1"

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
