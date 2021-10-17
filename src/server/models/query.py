import re
from datetime import datetime
from typing import Optional

from src.server.exceptions.invalid_request import InvalidRequest


class Query:
    app_id: str
    start_timestamp: Optional[datetime]
    end_timestamp: Optional[datetime]
    tag: Optional[str]
    pattern: Optional[str]

    def __init__(self, query_dict):
        try:
            start_timestamp = query_dict.get('start_timestamp')
            end_timestamp = query_dict.get('end_timestamp')
            pattern = query_dict.get('pattern')
            if (start_timestamp and not end_timestamp) or (end_timestamp and not start_timestamp):
                raise InvalidRequest
            if start_timestamp:
                start_timestamp = datetime.fromisoformat(start_timestamp)
            if end_timestamp:
                end_timestamp = datetime.fromisoformat(end_timestamp)
            if pattern:
                pattern = re.compile(pattern)
            self.app_id = query_dict['app_id']
            self.start_timestamp = start_timestamp
            self.end_timestamp = end_timestamp
            self.tag = query_dict.get('tag')
            self.pattern = pattern
        except (KeyError, ValueError, AttributeError, TypeError):
            raise InvalidRequest
