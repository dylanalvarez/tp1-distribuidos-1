import _queue
import logging
import signal
import socket
from multiprocessing import Process, Queue, Manager, Value

from src.server.invalid_request import InvalidRequest


def do_nothing(_, __):
    pass


def handle_client_requests(index, request_queue, generate_response, open_filenames, available_process_indices, must_exit):
    signal.signal(signal.SIGTERM, do_nothing)
    signal.signal(signal.SIGINT, do_nothing)
    while not must_exit.value:
        try:
            msg, client_sock = request_queue.get(timeout=1)
            try:
                client_sock.send(generate_response(msg[:-1], client_sock, open_filenames).encode('utf-8'))
            except InvalidRequest:
                client_sock.send(b'{"error": "invalid request"}\n')
            finally:
                available_process_indices.put(index)
            client_sock.close()
        except _queue.Empty:
            pass


class Server:
    def __init__(self, port, listen_backlog, generate_response):
        # Initialize src socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.settimeout(1.0)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.must_exit = Value('i', False)
        self.generate_response = generate_response
        self.processes = []
        self.process_queues = []
        self.manager = Manager()
        self.available_process_indices = self.manager.Queue()
        self.open_filenames = self.manager.dict()
        for index in range(10):
            self.available_process_indices.put(index)
            request_queue = Queue()
            self.process_queues.append(request_queue)
            process = Process(target=handle_client_requests, args=(index, request_queue, generate_response, self.open_filenames, self.available_process_indices, self.must_exit))
            process.start()
            self.processes.append(process)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        signal.signal(signal.SIGINT, self.exit_gracefully)

    def exit_gracefully(self, _, __):
        print("Exiting gracefully")
        self.must_exit.value = True

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        while not self.must_exit.value:
            client_sock = self.__accept_new_connection()
            if client_sock:
                self.__handle_client_connection(client_sock)
        self._server_socket.close()
        for process in self.processes:
            process.join()
        print("Exited gracefully!")

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        client_sock.settimeout(10)
        try:
            msg = ''
            while not (msg.endswith('\n') or bool(self.must_exit.value)):
                msg += client_sock.recv(10).decode('utf-8')
            if not msg.endswith('\n'):
                return
            try:
                index = self.available_process_indices.get_nowait()
                self.process_queues[index].put((msg, client_sock))
            except _queue.Full:
                client_sock.send(b'{"error": "service unavailable"}\n')
                client_sock.close()
        except OSError:
            logging.info("Error while reading socket {}".format(client_sock))

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info("Proceed to accept new connections")
        c = None
        address = None
        while not (c or bool(self.must_exit.value)):
            try:
                c, address = self._server_socket.accept()
            except socket.timeout as e:
                pass
        if not c or not address:
            return None
        logging.info('Got connection from {}'.format(address))
        return c
