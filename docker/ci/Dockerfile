# -----------------------------------------------------------------------------
# Образ для проверки репозитория перед ревью на CI-сервере.
#
# Образ общий для всех проектов.
# -----------------------------------------------------------------------------
FROM ubuntu:16.04

ENV LANG ru_RU.utf8

VOLUME /var/cache
VOLUME /root/project

RUN set -ex \
    # -------------------------------------------------------------------------
    # Установка необходимых системных пакетов.
    && apt-get update \
    && apt-get install --no-install-recommends --yes \
        ca-certificates \
        language-pack-ru \
        wget \
        curl \
        git \
        g++ \
        libpq-dev \
        libfreetype6-dev \
        libtiff5-dev \
        libssl-dev \
        libffi-dev \
        libxml2-dev \
        libxslt1-dev \
        libxmlsec1-dev \
        libsqlite3-dev \
        libreadline-dev \
        libbz2-dev \
        postgresql-contrib \
        redis-server \
    && apt autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    # -------------------------------------------------------------------------
    # Установка Python 2.7.14.
    && mkdir -p /usr/local/python/2.7 \
    && cd /tmp \
    && wget https://www.python.org/ftp/python/2.7.14/Python-2.7.14.tar.xz \
    && tar -xJf Python-2.7.14.tar.xz \
    && rm Python-2.7.14.tar.xz \
    && cd Python-2.7.14 \
    && ./configure \
        --prefix=/usr/local/python/2.7 \
        --enable-optimizations \
    && make \
    && make install \
    && cd \
    && rm -r /tmp/Python-2.7.14 \
    && export PATH=/usr/local/python/2.7/bin:$PATH \
    && curl https://bootstrap.pypa.io/get-pip.py | python2.7 \
    && pip2.7 install -U pip virtualenv Fabric \
    # -------------------------------------------------------------------------
    # Установка Python 3.6.4.
    && mkdir -p /usr/local/python/3.6 \
    && cd /tmp \
    && wget https://www.python.org/ftp/python/3.6.4/Python-3.6.4.tar.xz \
    && tar -xJf Python-3.6.4.tar.xz \
    && rm Python-3.6.4.tar.xz \
    && cd Python-3.6.4 \
    && ./configure \
        --prefix=/usr/local/python/3.6 \
        --enable-optimizations \
    && make \
    && make install \
    && cd \
    && rm -r /tmp/Python-3.6.4 \
    && export PATH=/usr/local/python/3.6/bin:$PATH \
    && pip3.6 install -U pip Fabric3
    # -------------------------------------------------------------------------

ENTRYPOINT /root/project/docker/ci/run-tasks.sh
