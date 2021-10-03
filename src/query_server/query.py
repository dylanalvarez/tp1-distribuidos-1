import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Query:
    app_id: str
    start_timestamp: Optional[datetime]
    end_timestamp: Optional[datetime]
    tag: Optional[str]
    pattern: Optional[str]


def parse_query(query_str):
    query_dict = json.loads(query_str)
    start_timestamp = query_dict.get('start_timestamp')
    end_timestamp = query_dict.get('end_timestamp')
    pattern = query_dict.get('pattern')
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
