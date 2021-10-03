import json

from src.server.log_message import log_message
from src.server.search_logs import search_logs


def process_message(message_string):
    message_dict = json.loads(message_string)
    log = message_dict.get('log')
    if log:
        log_message(log)
        return "LOGGED: {}\n".format(message_string)
    else:
        return "RESULT: {}\n".format(search_logs(message_dict['query']))
