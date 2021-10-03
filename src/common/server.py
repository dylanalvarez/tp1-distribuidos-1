import logging
import signal
import socket


class Server:
    def __init__(self, port, listen_backlog, generate_response):
        # Initialize src socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.settimeout(1.0)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.must_exit = False
        self.generate_response = generate_response
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        signal.signal(signal.SIGINT, self.exit_gracefully)

    def exit_gracefully(self, _, __):
        print("Exiting gracefully")
        self.must_exit = True

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        while not self.must_exit:
            client_sock = self.__accept_new_connection()
            if client_sock:
                self.__handle_client_connection(client_sock)
        self._server_socket.close()
        print("Exited gracefully!")

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            msg = ''
            while not (msg.endswith('\n') or self.must_exit):
                msg += client_sock.recv(10).decode('utf-8')
            if not msg.endswith('\n'):
                return
            client_sock.send(self.generate_response(msg[:-1], client_sock).encode('utf-8'))
        except OSError:
            logging.info("Error while reading socket {}".format(client_sock))
        finally:
            client_sock.close()

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
        while not (c or self.must_exit):
            try:
                c, address = self._server_socket.accept()
            except socket.timeout as e:
                pass
        if not c or not address:
            return None
        logging.info('Got connection from {}'.format(address))
        return c
