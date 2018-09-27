FROM postgres:10
MAINTAINER Lumi Kallioniemi <kallioniemi@pm.me>

ENV PYTHON_MAJOR 3
ENV POSTGIS_MAJOR 2.4

RUN apt-get update \
      && apt-cache showpkg postgresql-$PG_MAJOR-postgis-$POSTGIS_MAJOR \
      && apt-get install -y --no-install-recommends \
           postgresql-$PG_MAJOR-postgis-$POSTGIS_MAJOR \
           postgresql-$PG_MAJOR-postgis-$POSTGIS_MAJOR-scripts \
           postgis \
           python$PYTHON_MAJOR postgresql-plpython$PYTHON_MAJOR-$PG_MAJOR \
      && rm -rf /var/lib/apt/lists/* /var/cache/apt/* \
      && apt-get clean

RUN mkdir -p /docker-entrypoint-initdb.d
COPY ./initdb-postgis.sh /docker-entrypoint-initdb.d/postgis.sh
COPY ./update-postgis.sh /usr/local/bin
COPY ./conf.sql /docker-entrypoint-initdb.d/conf.sql

