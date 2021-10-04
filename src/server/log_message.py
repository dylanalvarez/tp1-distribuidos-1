import json
import os
import time

from src.server.get_filename import get_filename
from src.server.log import parse_log


def log_message(log_dict, open_filenames):
    log = parse_log(log_dict)
    dir_name = f'logs/{log.app_id}'
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    filename = get_filename(log.app_id, log.timestamp)
    while open_filenames.get(filename):
        time.sleep(1)
    with open(filename, 'a+') as file:
        file.write(f'{json.dumps(log_dict)}\n')
    open_filenames[filename] = False
