FROM python:3.9

# set working directory
WORKDIR /movie-scrapper

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

# install google chrome
RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get -yqq update && \
    apt-get -yqq install google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# install firefox
RUN apt-get -qy --no-install-recommends install \
     $(apt-cache depends firefox | grep Depends | sed "s/.*ends:\ //" | tr '\n' ' ') \
  && rm -rf /var/lib/apt/lists/* \
  && cd /tmp \
  && wget --no-check-certificate -O firefox-esr.tar.bz2 \
    'https://download.mozilla.org/?product=firefox-esr-latest&os=linux64&lang=en-US' \
  && tar -xjf firefox-esr.tar.bz2 -C /opt/ \
  && ln -s /opt/firefox/firefox /usr/bin/firefox \
  && rm -f /tmp/firefox-esr.tar.bz2

# configure virtual display
RUN set -e
RUN echo "Starting X virtual framebuffer (Xvfb) in background..."
RUN Xvfb -ac :99 -screen 0 1280x1024x16 > /dev/null 2>&1 &
RUN export DISPLAY=:99
RUN exec "$@"

# download drivers
RUN mkdir drivers/
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux32.tar.gz
RUN tar -xvzf geckodriver-v0.30.0-linux32.tar.gz
RUN chmod +x geckodriver
RUN mv geckodriver drivers/
RUN rm -rf geckodriver-v0.30.0-linux32.tar.gz
RUN wget https://chromedriver.storage.googleapis.com/2.44/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip
RUN chmod +x chromedriver
RUN mv chromedriver drivers/
RUN rm -rf chromedriver_linux64.zip

RUN mkdir app/
COPY app/ app/
COPY start_server.sh .
