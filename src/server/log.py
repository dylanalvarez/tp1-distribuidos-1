from dataclasses import dataclass
from datetime import datetime
from typing import List

from src.server.exceptions.invalid_request import InvalidRequest


@dataclass
class Log:
    app_id: str
    message: str
    log_tags: List[str]
    timestamp: datetime


def parse_log(log_dict):
    try:
        return Log(
            app_id=str(log_dict['app_id']),
            message=str(log_dict['message']),
            log_tags=[str(tag) for tag in log_dict['log_tags']],
            timestamp=datetime.fromisoformat(log_dict['timestamp'])
        )
    except (KeyError, ValueError, TypeError):
        raise InvalidRequest
