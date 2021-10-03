import os

from src.common.get_filename import get_filename
from src.common.log import parse_log


def log_message(log_str):
    log = parse_log(log_str)
    dir_name = f'logs/{log.app_id}'
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    with open(get_filename(log.app_id, log.timestamp), 'a+') as file:
        file.write(f'{log_str}\n')
