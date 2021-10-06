#!/usr/bin/env python3
import json
import socket

from src.common.initialize_config import initialize_config
from src.common.initialize_log import initialize_log


def receive(socket):
    msg = ''
    while not msg.endswith('\n'):
        msg += socket.recv(10).decode('utf-8')
    return msg


def send(message, config_params):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(10)
            s.connect((config_params["server_ip"], config_params["server_port"]))
            s.sendall(f'{message}\n'.encode('utf-8'))
            print('Sent', message)
            print('Received', receive(s))
            s.close()
        except socket.timeout:
            print("Connection timed out (forgot a newline at the end?)")


def main():
    config_params = initialize_config([('server_port', int), ('server_ip', str), ('logging_level', str)])
    initialize_log(config_params["logging_level"])

    # invalid messages
    send('asd', config_params)
    send('["asd"]', config_params)
    send('{"asd": 5}', config_params)
    # invalid logs
    send('{"log": 123}', config_params)
    send('{"log": []}', config_params)
    send('{"log": {"app_id": "holi"}}', config_params)
    send('{"log": {"app_id": "holi", "message": "holi"}}', config_params)
    send('{"log": {"app_id": "holi", "message": "holi", "timestamp": "2021-10-19T22:56:23-03:00"}}', config_params)
    send('{"log": {"app_id": "holi", "message": "holi", "timestamp": "2021-10-19T22:56:23-03:00", "log_tags": 2}}', config_params)
    send('{"log": {"app_id": "holi", "message": "holi", "timestamp": "a timestamp", "log_tags": ["warn"]}}', config_params)
    # invalid queries
    send('{"query": 123}', config_params)
    send('{"query": []}', config_params)
    send('{"query": {}]}', config_params)
    send('{"query": {"tag": "error"}]}', config_params)
    send('{"query": {"tag": "error", "pattern": "([m])\w+"}}', config_params)
    send('{"query": {"app_id": "holi", "start_timestamp": "2021-10-19T22:56:23-03:00"}}', config_params)
    send('{"query": {"app_id": "holi", "end_timestamp": "2021-10-19T22:56:23-03:00"}}', config_params)
    # valid logs
    send('{"log": {"app_id": "holi", "message": "holi", "timestamp": "2021-01-01T00:00:00-03:00", "log_tags": ["error"]}}', config_params)
    send('{"log": {"app_id": "holi", "message": "123", "timestamp": "2021-01-01T01:00:00-03:00", "log_tags": []}}', config_params)
    send('{"log": {"app_id": "hola", "message": "", "timestamp": "2021-01-01T02:00:00-03:00", "log_tags": ["warn", "error"]}}', config_params)
    send(json.dumps({"log": {"app_id": "hola\nmundo", "message": "hola\nmundo", "timestamp": "2021-01-01T02:00:00-03:00", "log_tags": ["warn", "error"]}}), config_params)
    # valid queries
    send('{"query": {"app_id": "holi", "start_timestamp": "2021-01-01T00:00:00-03:00", "end_timestamp": "2021-01-01T00:30:00-03:00"}}', config_params)
    send('{"query": {"app_id": "holi", "start_timestamp": "2021-01-01T00:30:00-03:00", "end_timestamp": "2021-01-01T01:30:00-03:00"}}', config_params)
    send('{"query": {"app_id": "holi", "start_timestamp": "2021-01-01T00:00:00-03:00", "end_timestamp": "2021-01-01T01:30:00-03:00", "tag": "error"}}', config_params)
    send('{"query": {"app_id": "hola"}}', config_params)
    send('{"query": {"app_id": "holi", "pattern": ' + json.dumps(r'\d+') + '}}', config_params)
    send('{"query": {"app_id": "hole", "pattern": ' + json.dumps(r'\d+') + '}}', config_params)


if __name__ == "__main__":
    main()
