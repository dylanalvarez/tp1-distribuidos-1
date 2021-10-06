FROM python:3.8.10-slim
COPY src/__init__.py src/__init__.py
COPY src/client2/config.ini /config.ini
COPY src/client2 src/client
COPY src/common src/common
ENTRYPOINT ["/bin/sh"]