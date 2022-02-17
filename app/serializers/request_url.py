from pydantic import BaseModel


class InputUrl(BaseModel):
    encoded_url: str
    q_string: str
    q_imdb: str
