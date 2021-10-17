import json

from src.server.exceptions.invalid_request import InvalidRequest
from src.server.log_message import log_message
from src.server.search_logs import search_logs


def process_message(message_string, open_filenames):
    try:
        message_dict = json.loads(message_string)
    except json.decoder.JSONDecodeError:
        raise InvalidRequest
    if type(message_dict) is not dict:
        raise InvalidRequest
    if log := message_dict.get('log'):
        log_message(log, open_filenames)
        return "LOGGED: {}\n".format(message_string)
    elif query := message_dict.get('query'):
        return "RESULT: {}\n".format(search_logs(query, open_filenames))
    else:
        raise InvalidRequest
