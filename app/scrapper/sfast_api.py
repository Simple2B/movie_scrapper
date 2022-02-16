from fastapi import FastAPI
from fastapi.responses import FileResponse
import requests


app = FastAPI()

@app.get("/")
async def root():  # return of the root link of the api
  return FileResponse('docs.pdf')

@app.get("/get_urls_file")
def get_urls_file():
    return FileResponse("text_files/full_urls_clean.txt")

@app.get("/dummy")
def dummy_endpoint():
    return {"list_of_links": "CloudFlare", "list_of_links1": "PageNotTreated"}, 200

@app.post("/input_movies")
def input_movies_urls(movie_urls):
    f = open("movie_urls.txt", "w")
    f.write(str(movie_urls))
    f.close()
    return {"movie_urls": str(movie_urls)}, 200
