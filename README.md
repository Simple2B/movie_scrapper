# Movie link scrapper
## Requirements:
- Python 3.9
- [Poetry](https://python-poetry.org/) is recommended
- FastApi
- Uvicorn
- Pydantic
- Selenium
- python-dotenv
- Loguru
- Requests
- random-user-agent
- beautifulsoup4
- webdriver-manager
## Setup
### Start application
```
$ cd cyberlocker-api
```
```
$ poetry run uvicorn app.main:app
```
[Enjoy](http://127.0.0.1:8000)
### Run docker container
```
$ cd cyberlocker-api
```
- Build docker container
```
$ docker-compose build
```
- Up docker-container
```
$ docker-compose up -d
```
- Check if docker-container is up
```
$ docker-compose ps
```
[Enjoy](http://127.0.0.1:8000)
## Additional functionality
### You can use inside client
- Scrap from single link
```
$ url="host:/domain.tld/path" python app/client.py scrap_url
```
- Scrap from links list in .txt format
```
$ input_filepath="temp/target_links.txt" python app/client.py scrap_file
```