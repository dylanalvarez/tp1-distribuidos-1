import json
from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Log:
    app_id: str
    message: str
    log_tags: List[str]
    timestamp: datetime


def parse_log(log_dict):
    return Log(
        app_id=log_dict['app_id'],
        message=log_dict['message'],
        log_tags=log_dict['log_tags'],
        timestamp=datetime.fromisoformat(log_dict['timestamp'])
    )
