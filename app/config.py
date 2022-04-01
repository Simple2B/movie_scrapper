import os
from typing import List, Union
from pydantic import AnyHttpUrl, BaseSettings, validator
from dotenv import load_dotenv


class Settings(BaseSettings):
    load_dotenv()
    DEBUG: bool = True if os.getenv("DEBUG", "0") == "1" else False
    APP_NAME: str = "FastAPI_scrapper"
    APP_DESCRIPTION: str = ""
    APP_VERSION: str = "0.1.1"
    DOCS_URL: str = "/"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "ERROR")
    JSON_LOGS: bool = True if os.getenv("JSON_LOGS", "0") == "1" else False
    OUTPUT_FILE: str = os.path.join(BASE_DIR, "video_urls.xlsx")
    IGNORED_DOMAINS: list[AnyHttpUrl] = [
        "https://api.whatsapp.com",
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
