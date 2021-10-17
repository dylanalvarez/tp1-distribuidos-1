import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.server.exceptions.invalid_request import InvalidRequest


@dataclass
class Query:
    app_id: str
    start_timestamp: Optional[datetime]
    end_timestamp: Optional[datetime]
    tag: Optional[str]
    pattern: Optional[str]


def parse_query(query_dict):
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
        return Query(
            app_id=query_dict['app_id'],
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            tag=query_dict.get('tag'),
            pattern=pattern,
        )
    except (KeyError, ValueError, AttributeError, TypeError):
        raise InvalidRequest
