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
## Setup
### Start docker container
```
$ cd cyberlocker-api
```
```
$ docker-compose up -d
```
### Check that container is running
```
$ docker-compose ps
```
## Additional functionality
### You can use inside client
- Scrap from single link
```
$ docker-compose exec app bash -c "url='[website]' python app/client.py scrap_url
```
- Scrap from links list in .txt format
```
$ docker-compose exec app bash -c "input_filepath='[path-to-target-links-list.txt]' urls_output_filepath='[path-to-result-lists.txt]' python app/client.py scrap_file"
```
### Copy results to you system
```
$ sudo docker cp 61bfcf6f3fa6:/movie-scrapper/data/urls.csv /mnt/c/Coding/Projects/Simple2B/movie_scrapper/movie_scrapper/data/urls.csv
```
```
$ sudo docker cp 61bfcf6f3fa6:/movie-scrapper/data/cyberlockers.csv /mnt/c/Coding/Projects/Simple2B/movie_scrapper/movie_scrapper/data/cyberlockers.csv
```
```
$ sudo docker cp 61bfcf6f3fa6:/movie-scrapper/data/unique_cyberlockers.csv /mnt/c/Coding/Projects/Simple2B/movie_scrapper/movie_scrapper/data/unique_cyberlockers.csv
```