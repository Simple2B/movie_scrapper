FROM python:3.9

# set working directory
WORKDIR /app

# set environment varibles
ENV PYTHONFAULTHANDLER 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONHASHSEED random
ENV PIP_NO_CACHE_DIR off
ENV PIP_DISABLE_PIP_VERSION_CHECK on

# install poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
ENV PATH="${PATH}:/root/.poetry/bin"
COPY poetry.lock .
COPY pyproject.toml .

RUN POETRY_VIRTUALENVS_CREATE=false poetry install --no-dev --no-interaction --no-ansi
# install manually all the missing libraries
#RUN apt-get install -y gconf-service libasound2 libatk1.0-0 libcairo2 libcups2 libfontconfig1 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils
#RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
#RUN apt install ./google-chrome-stable_current_amd64.deb
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable
RUN apt-get -y autoremove

COPY . .