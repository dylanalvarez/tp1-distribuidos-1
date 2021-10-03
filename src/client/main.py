#!/usr/bin/env python3
import json
import socket

from src.common.initialize_config import initialize_config
from src.common.initialize_log import initialize_log

logs = map(json.dumps, [
    {'log': {
        'app_id': 'holi',
        'message': 'mensaje1\n',
        'log_tags': ['warn', 'error'],
        'timestamp': '2021-09-19T22:56:23.713555-03:00'
    }},
    {'log': {
        'app_id': 'holi',
        'message': 'mensaje\n2',
        'log_tags': [],
        'timestamp': '2021-09-19T22:54:23.713555-03:00'
    }},
    {'log': {
        'app_id': 'hola',
        'message': '\nmensaje',
        'log_tags': ['warn', 'error'],
        'timestamp': '2021-09-19T23:56:23.713555-03:00'
    }}
])

queries = map(json.dumps, [
    {'query': {
        'app_id': 'holi',
        'tag': 'warn',
        'start_timestamp': '2021-09-02T22:56:23.713555-03:00',
        'end_timestamp': '2021-09-26T22:56:23.713555-03:00'
    }},
    {'query': {
        'app_id': 'holi',
        'start_timestamp': '2021-09-02T22:56:23.713555-03:00',
        'end_timestamp': '2021-09-26T22:56:23.713555-03:00'
    }},
    {'query': {
        'app_id': 'hola',
        'pattern': r'([m])\w+',
    }},
])


def main():
    config_params = initialize_config([('server_port', int), ('server_ip', str), ('logging_level', str)])
    initialize_log(config_params["logging_level"])

    for log in logs:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect((config_params["server_ip"], config_params["server_port"]))
            s.sendall(f'{log}\n'.encode('utf-8'))
            data = s.recv(1024)
            print('Received', repr(data))
            s.close()

    for query in queries:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect((config_params["server_ip"], config_params["server_port"]))
            s.sendall(f'{query}\n'.encode('utf-8'))
            data = s.recv(10240)
            print('Received', repr(data))
            s.close()


if __name__ == "__main__":
    main()
