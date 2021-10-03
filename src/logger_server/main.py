#!/usr/bin/env python3
import logging

from src.common.initialize_config import initialize_config
from src.common.initialize_log import initialize_log
from src.logger_server.log_message import log_message
from src.common.server import Server


def generate_response(msg, client_sock):
    logging.info('Message received from connection {}. Msg: {}'.format(client_sock.getpeername(), msg))
    log_message(msg)
    return "LOGGED: {}\n".format(msg)


def main():
    config_params = initialize_config([('server_port', int), ('server_listen_backlog', int), ('logging_level', str)])
    initialize_log(config_params["logging_level"])

    # Log config parameters at the beginning of the program to verify the configuration
    # of the component
    logging.debug("Server configuration: {}".format(config_params))

    # Initialize src and start src loop
    server = Server(config_params["server_port"], config_params["server_listen_backlog"], generate_response)
    server.run()


if __name__ == "__main__":
    main()
