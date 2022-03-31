from pydantic import AnyHttpUrl, BaseModel, validator


class Urls(BaseModel):
    target_ulr: AnyHttpUrl
    urls: list[AnyHttpUrl]
    error: str = ""
