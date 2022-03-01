import os
from fastapi import APIRouter  # , Depends
# from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
# from app.services import AuthService, get_current_user
# from app.serializers import InputUrl
from app.scrapper.main import write_links
from app.config import settings
import base64
from typing import Optional

router = APIRouter(prefix="/scrap")
text_files_path = str(os.path.join(settings.BASE_DIR, "scrapper/text_files/"))


@router.get("/")
async def root():  # return of the root link of the api
    return {"routes to visit": ("/get_urls_file", "/dummy", "/input_movies")}


@router.get("/get_urls_file")
def get_urls_file():
    write_links(["https://prmovies.com/american-siege-2021-Watch-online-on-prmovies/"])
    # return FileResponse("text_files/full_urls_clean.txt")
    return FileResponse(text_files_path+"/potential_cyberlockers_full_urls.txt")


@router.get("/dummy")
def dummy_endpoint():
    return {"list_of_links": "CloudFlare", "list_of_links1": "PageNotTreated"}, 200


@router.post("/generalist/{target_link_encoded}")
def input_movies_urls(target_link_encoded, q_string: Optional[str], q_imdb: Optional[str]):
    if q_string:
        movie_name = q_string
    else:
        movie_name = ''
    if q_imdb:
        imdb = q_imdb
    else:
        imdb = ''

    decoded_url = base64.b64decode(target_link_encoded).decode("utf-8")
    f = open("movie_urls.txt", "a")
    f.write(str(target_link_encoded))
    f.close()
    list_of_links = write_links([decoded_url])
    return {"list_of_links": list_of_links, "movie_name": movie_name, "imdb": imdb}, 200
