from datetime import datetime
from typing import List

from src.server.exceptions.invalid_request import InvalidRequest


class Log:
    app_id: str
    message: str
    log_tags: List[str]
    timestamp: datetime

    def __init__(self, log_dict):
        try:
            self.app_id = str(log_dict['app_id'])
            self.message = str(log_dict['message'])
            self.log_tags = [str(tag) for tag in log_dict['log_tags']]
            self.timestamp = datetime.fromisoformat(log_dict['timestamp'])
        except (KeyError, ValueError, TypeError):
            raise InvalidRequest
