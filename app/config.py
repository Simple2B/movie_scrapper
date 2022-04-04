import os
from typing import List, Union
from pydantic import AnyHttpUrl, BaseSettings, validator
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    DEBUG: bool = os.getenv("DEBUG", "0") == "1"
    APP_NAME: str = "FastAPI_scrapper"
    APP_DESCRIPTION: str = ""
    APP_VERSION: str = "0.1.1"
    OPENAPI_URL: str = "/api/openapi.json"
    DOCS_URL: str = "/api/docs"
    SWAGGER_UI_OAUTH2_REDIRECT_URL: str = "/api/docs/oauth2-redirect"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    STORAGE_FOLDER: str = "data"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "ERROR")
    JSON_LOGS: bool = os.getenv("JSON_LOGS", "0") == "1"
    OUTPUT_FILE: str = os.path.join(
        os.path.join(BASE_DIR, STORAGE_FOLDER), "video_urls.xlsx"
    )
    IGNORED_DOMAINS: list[str] = [
        "whatsapp.com",
        "facebook.com",
    ]

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
