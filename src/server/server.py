import _queue
import logging
import signal
import socket
from multiprocessing import Manager, Value

from src.server.worker import Worker


class Server:
    def __init__(self, port, listen_backlog, worker_count):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.settimeout(1.0)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)

        self.manager = Manager()
        self.available_worker_ids = self.manager.Queue()
        self.open_filenames = self.manager.dict()
        self.must_exit = Value('i', False)

        self.workers = [Worker(index, self.available_worker_ids, self.open_filenames, self.must_exit)
                        for index in range(worker_count)]

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communication
        finishes, servers starts to accept new connections again
        """
        self._set_sigterm_callback()
        for worker in self.workers:
            worker.start()

        while not self.must_exit.value:
            client_socket = self._accept_new_connection()
            if client_socket:
                self._handle_client_connection(client_socket)

        self._server_socket.close()
        for worker in self.workers:
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
            message = ''
            while not (message.endswith('\n') or bool(self.must_exit.value)):
                message += client_socket.recv(10).decode('utf-8')
            if not message.endswith('\n'):
                return
            try:
                index = self.available_worker_ids.get_nowait()
                self.workers[index].request_queue.put((message, client_socket))
            except _queue.Empty:
                client_socket.sendall(b'{"error": "service unavailable"}\n')
                client_socket.close()
        except OSError:
            logging.info("Error while reading socket {}".format(client_socket))

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
