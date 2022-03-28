import os
from typing import List, Union
from pydantic import AnyHttpUrl, BaseSettings, validator


class Settings(BaseSettings):
    SERVER_NAME: str = "FastAPI_scrapper"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    FILES_PATH = os.path.join(BASE_DIR, "temp/")
    if not os.path.isdir(FILES_PATH):
        os.mkdir(FILES_PATH)

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