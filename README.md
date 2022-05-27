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
- Install [poetry](https://python-poetry.org/docs/)
- Install project dependencies
```
$ poetry install
```
### Start application and [Enjoy](http://127.0.0.1:8090/api/docs)
- Go to working directory
```
$ cd cyberlocker-api
```
- Start application
```
$ poetry run uvicorn app.main:app
```
### Run docker container and [Enjoy](http://127.0.0.1:8000/api/docs)
- Go to working directory
```
$ cd cyberlocker-api
```
- Build docker container
```
$ docker-compose build
```
- Up docker container
```
$ docker-compose up -d
```
- Check if docker container is up
```
$ docker-compose ps
```
## Additional functionality
### You can use inside client
- Scrap from single link
```
$ url="host:/domain.tld/path" python client.py scrap_url
```
- Scrap from links list in .txt format
```
$ input_filepath="temp/target_links.txt" python client.py scrap_file
```