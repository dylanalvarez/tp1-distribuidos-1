FROM python:3.8.10-slim
COPY src/__init__.py /src/__init__.py
COPY src/query_server/config.ini /config.ini
COPY src/query_server /src/query_server
COPY src/common /src/common
ENTRYPOINT ["/bin/sh"]