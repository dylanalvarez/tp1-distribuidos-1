import _queue
import itertools
import json
import logging
import signal
import socket
from multiprocessing import Manager, Value

from src.common.receive_line import receive_line
from src.common.send_line import send_line
from src.server.log_worker import LogWorker
from src.server.query_worker import QueryWorker


class Server:
    def __init__(self, port, listen_backlog, log_worker_count, query_worker_count):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.settimeout(1.0)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)

        self.manager = Manager()
        self.available_log_worker_ids = self.manager.Queue()
        self.available_query_worker_ids = self.manager.Queue()
        self.open_filenames = self.manager.dict()
        self.must_exit = Value('i', False)

        self.log_workers = [LogWorker(index, self.available_log_worker_ids, self.open_filenames, self.must_exit)
                            for index in range(log_worker_count)]
        self.query_workers = [QueryWorker(index, self.available_query_worker_ids, self.open_filenames, self.must_exit)
                              for index in range(query_worker_count)]

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communication
        finishes, servers starts to accept new connections again
        """
        self._set_sigterm_callback()
        for worker in itertools.chain(self.log_workers, self.query_workers):
            worker.start()

        while not self.must_exit.value:
            client_socket = self._accept_new_connection()
            if client_socket:
                self._handle_client_connection(client_socket)

        self._server_socket.close()
        for worker in itertools.chain(self.log_workers, self.query_workers):
            worker.join()
        print("Exited gracefully!")

    def _handle_client_connection(self, client_socket):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        client_socket.settimeout(10)
        try:
            message = receive_line(client_socket)
            if not message:
                return
            try:
                self._handle_message(message, client_socket)
            except _queue.Empty:
                self._send_service_unavailable(client_socket)
        except OSError:
            logging.info("Error while reading socket {}".format(client_socket))

    def _handle_message(self, message_string, client_socket):
        try:
            message_dict = json.loads(message_string)
        except json.decoder.JSONDecodeError:
            return self._send_invalid_request(client_socket)
        if type(message_dict) is not dict:
            return self._send_invalid_request(client_socket)
        if log_dict := message_dict.get('log'):
            index = self.available_log_worker_ids.get_nowait()
            self.log_workers[index].request_queue.put((log_dict, client_socket))
        elif query_dict := message_dict.get('query'):
            index = self.available_query_worker_ids.get_nowait()
            self.query_workers[index].request_queue.put((query_dict, client_socket))
        else:
            self._send_invalid_request(client_socket)

    @staticmethod
    def _send_invalid_request(client_socket):
        send_line('{"error": "invalid request"}', client_socket)
        client_socket.close()

    @staticmethod
    def _send_service_unavailable(client_socket):
        send_line('{"error": "service unavailable"}', client_socket)
        client_socket.close()

    def _accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info("Proceed to accept new connections")
        client_socket = None
        address = None
        while not (client_socket or bool(self.must_exit.value)):
            try:
                client_socket, address = self._server_socket.accept()
            except socket.timeout:
                pass
        if not client_socket or not address:
            return None
        logging.info('Got connection from {}'.format(address))
        return client_socket

    def _set_sigterm_callback(self):
        signal.signal(signal.SIGTERM, self._exit_gracefully)
        signal.signal(signal.SIGINT, self._exit_gracefully)

    def _exit_gracefully(self, _, __):
        print("Exiting gracefully")
        self.must_exit.value = True
