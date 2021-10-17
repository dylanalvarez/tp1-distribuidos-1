import json
import os
import time

from src.common.generate_filename import generate_filename
from src.server.models.log import Log


def log_message(log_dict, open_filenames):
    log = Log(log_dict)
    dir_name = f'logs/{log.app_id}'
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    filename = generate_filename(log.app_id, log.timestamp)
    while open_filenames.get(filename):
        time.sleep(1)
    open_filenames[filename] = True
    with open(filename, 'a+') as file:
        file.write(f'{json.dumps(log_dict)}\n')
    open_filenames[filename] = False
