import os
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    SERVER_NAME: str = "FastAPI_scrapper" #os.environ.get("SERVER_NAME") # "FastAPI scrapper"
    #SERVER_HOST: AnyHttpUrl
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    ENV: str = "production"

    JWT_SECRET: str = "dummy_secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXP: str = "3600"

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True


settings = Settings(_env_file=".env", _env_file_encoding="utf-8")
