import json
import os

from src.server.get_filename import get_filename
from src.server.log import parse_log


def log_message(log_dict):
    log = parse_log(log_dict)
    dir_name = f'logs/{log.app_id}'
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    with open(get_filename(log.app_id, log.timestamp), 'a+') as file:
        file.write(f'{json.dumps(log_dict)}\n')
