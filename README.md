# FastApi.app

# Scrapping url. You need to specify url.

`url="https://bloomovie.com/bull-2022-watch-online-free/" python app/client.py scrap_url`

# Docker. Scrapping url. You need to specify url.

`docker-compose exec app bash -c "url="https://bloomovie.com/bull-2022-watch-online-free/" python app/client.py scrap_url"`

# Scrapping a file with urls. You need to specify input_filepath and you can specify urls_output_filepath, cyberlockers_output_filepath, unique_cyberlockers_output_filepath. If output_filepath for some file is not provided, then the file will be saved to input_filepath directory.

`"input_filepath="data/target_links.txt" urls_output_filepath="data/urls.csv" python app/client.py scrap_file`

# Docker. Scrapping a file with urls. You need to specify input_filepath and you can specify urls_output_filepath, cyberlockers_output_filepath, unique_cyberlockers_output_filepath. If output_filepath for some file is not provided, then the file will be saved to input_filepath direccory.

# docker-compose exec app bash -c "input_filepath="data/target_links.txt" urls_output_filepath="data/urls.csv" python app/client.py scrap_file"

# Copying files from inside docker container to local system.

`sudo docker cp 61bfcf6f3fa6:/movie-scrapper/data/urls.csv /mnt/c/Coding/Projects/Simple2B/movie_scrapper/movie_scrapper/data/urls.csv`
`sudo docker cp 61bfcf6f3fa6:/movie-scrapper/data/cyberlockers.csv /mnt/c/Coding/Projects/Simple2B/movie_scrapper/movie_scrapper/data/cyberlockers.csv`
`sudo docker cp 61bfcf6f3fa6:/movie-scrapper/data/unique_cyberlockers.csv /mnt/c/Coding/Projects/Simple2B/movie_scrapper/movie_scrapper/data/unique_cyberlockers.csv`
