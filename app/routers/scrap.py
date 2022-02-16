import os
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
#from app.services import AuthService, get_current_user
from app.serializers import UserCreate, User, Token
from app.scrapper.main import write_links
from app.config import settings

router = APIRouter(prefix="/scrap")
text_files_path = str(os.path.join(settings.BASE_DIR, "scrapper/text_files/"))


@router.get("/")
async def root():  # return of the root link of the api
  return {"routes to visit": ("/get_urls_file", "/dummy", "/input_movies")}

@router.get("/get_urls_file")
def get_urls_file():
    write_links(["https://prmovies.com/american-siege-2021-Watch-online-on-prmovies/"])
    #return FileResponse("text_files/full_urls_clean.txt")
    return FileResponse(text_files_path+"/potential_cyberlockers_full_urls.txt")
    

@router.get("/dummy")
def dummy_endpoint():
    return {"list_of_links": "CloudFlare", "list_of_links1": "PageNotTreated"}, 200

@router.post("/input_movies")
def input_movies_urls(movie_urls):
    f = open("movie_urls.txt", "w")
    f.write(str(movie_urls))
    f.close()
    return {"movie_urls": str(movie_urls)}, 200
