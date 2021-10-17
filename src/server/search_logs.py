import json
import os
import time
from datetime import timedelta

from src.server.exceptions.app_id_does_not_exist import AppIdDoesNotExist
from src.server.get_filename import get_filename
from src.server.models.log import Log
from src.server.models.query import Query


def get_filenames(app_id, start_timestamp, end_timestamp):
    delta = end_timestamp - start_timestamp
    timestamps = [start_timestamp + timedelta(hours=i) for i in range(delta.seconds // 3600 + 1)]
    return [get_filename(app_id, timestamp) for timestamp in timestamps]


def does_match(log, query):
    if query.start_timestamp:
        if not query.start_timestamp <= log.timestamp <= query.end_timestamp:
            return False
    if query.tag:
        if query.tag not in log.log_tags:
            return False
    if query.pattern:
        if not query.pattern.search(log.message):
            return False
    return True


def search_logs(query_dict, open_filenames):
    query = Query(query_dict)
    result = []
    if query.start_timestamp:
        filenames = get_filenames(query.app_id, query.start_timestamp, query.end_timestamp)
    else:
        try:
            filenames = [f'logs/{query.app_id}/{filename}' for filename in os.listdir(f'logs/{query.app_id}')]
        except FileNotFoundError:
            raise AppIdDoesNotExist
    for filename in filenames:
        try:
            while open_filenames.get(filename):
                time.sleep(1)
            open_filenames[filename] = True
            with open(filename) as file:
                for line in file:
                    line = line[:-1]
                    log = Log(json.loads(line))
                    if does_match(log, query):
                        result.append((line, log.timestamp))
        except FileNotFoundError:
            pass
        finally:
            open_filenames[filename] = False
    result = sorted(result, key=lambda line_with_timestamp: line_with_timestamp[1])
    return f'[{", ".join([line_with_timestamp[0] for line_with_timestamp in result])}]'
