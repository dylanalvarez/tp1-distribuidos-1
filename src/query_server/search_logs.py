import os
from datetime import timedelta

from src.common.get_filename import get_filename
from src.common.log import parse_log
from src.query_server.query import parse_query


def get_filenames(app_id, start_timestamp, end_timestamp):
    delta = end_timestamp - start_timestamp
    timestamps = [start_timestamp + timedelta(hours=i) for i in range(delta.days * 24 + 1)]
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


def search_logs(query_str):
    query = parse_query(query_str)
    result = []
    if query.start_timestamp:
        filenames = get_filenames(query.app_id, query.start_timestamp, query.end_timestamp)
    else:
        try:
            filenames = [f'logs/{query.app_id}/{filename}' for filename in os.listdir(f'logs/{query.app_id}')]
        except FileNotFoundError:
            filenames = []
    for filename in filenames:
        try:
            with open(filename) as file:
                for line in file:
                    log = parse_log(line)
                    if does_match(log, query):
                        result.append(line[:-1])
        except FileNotFoundError:
            pass
    return f'[{", ".join(result)}]'
