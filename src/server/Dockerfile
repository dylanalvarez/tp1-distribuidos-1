FROM python:3.8.10-slim
COPY src/__init__.py /src/__init__.py
COPY src/server/config.ini /config.ini
COPY src/server /src/server
COPY src/common /src/common
ENTRYPOINT ["/bin/sh"]