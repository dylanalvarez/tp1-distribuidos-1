#!/usr/bin/env python3
import logging

from src.common.initialize_config import initialize_config
from src.common.initialize_log import initialize_log
from src.server.server import Server


def main():
    config_params = initialize_config([
        ('server_port', int),
        ('server_listen_backlog', int),
        ('logging_level', str),
        ('log_worker_count', int),
        ('query_worker_count', int)
    ])
    initialize_log(config_params["logging_level"])

    # Log config parameters at the beginning of the program to verify the configuration
    # of the component
    logging.debug("Server configuration: {}".format(config_params))

    # Initialize src and start src loop
    server = Server(
        config_params["server_port"],
        config_params["server_listen_backlog"],
        config_params['log_worker_count'],
        config_params['query_worker_count']
    )
    server.run()


if __name__ == "__main__":
    main()
