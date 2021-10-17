import _queue
import logging
import signal
from abc import abstractmethod
from multiprocessing import Process, Queue

from src.common.do_nothing import do_nothing
from src.server.exceptions.app_id_does_not_exist import AppIdDoesNotExist
from src.server.exceptions.invalid_request import InvalidRequest


class Worker:
    def __init__(self, id, available_worker_ids, open_filenames, must_exit):
        self.id = id
        self.available_worker_ids = available_worker_ids
        self.open_filenames = open_filenames
        self.must_exit = must_exit
        self.request_queue = Queue()
        self.process = None

    def start(self):
        self.available_worker_ids.put(self.id)
        self.process = Process(
            target=self._handle_client_requests,
            args=(self.id, self.request_queue, self.open_filenames, self.available_worker_ids, self.must_exit)
        )
        self.process.start()

    def join(self):
        if self.process:
            self.process.join()

    @classmethod
    def _handle_client_requests(cls, worker_id, request_queue, open_filenames, available_process_indices, must_exit):
        Worker._set_sigterm_callback()
        while not must_exit.value:
            try:
                msg, client_socket = request_queue.get(timeout=1)
                try:
                    logging.info('Message received from connection {}. Msg: {}'.format(client_socket.getpeername(), msg))
                    client_socket.sendall(cls._process_message(msg, open_filenames).encode('utf-8'))
                except InvalidRequest:
                    client_socket.sendall(b'{"error": "invalid request"}\n')
                except AppIdDoesNotExist:
                    client_socket.sendall(b'{"error": "app id does not exist"}\n')
                finally:
                    available_process_indices.put(worker_id)
                client_socket.close()
            except _queue.Empty:
                pass
        logging.debug(f'WORKER {worker_id} exiting gracefully')

    @staticmethod
    @abstractmethod
    def _process_message(message_dict, open_filenames):
        pass

    @staticmethod
    def _set_sigterm_callback():
        signal.signal(signal.SIGTERM, do_nothing)
        signal.signal(signal.SIGINT, do_nothing)
