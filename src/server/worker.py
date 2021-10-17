import _queue
import json
import logging
import signal
from multiprocessing import Process, Queue

from src.common.do_nothing import do_nothing
from src.server.exceptions.app_id_does_not_exist import AppIdDoesNotExist
from src.server.exceptions.invalid_request import InvalidRequest
from src.server.log_message import log_message
from src.server.search_logs import search_logs


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
            target=Worker._handle_client_requests,
            args=(self.id, self.request_queue, self.open_filenames, self.available_worker_ids, self.must_exit)
        )
        self.process.start()

    def join(self):
        if self.process:
            self.process.join()

    @staticmethod
    def _handle_client_requests(worker_id, request_queue, open_filenames, available_process_indices, must_exit):
        Worker._set_sigterm_callback()
        while not must_exit.value:
            try:
                msg, client_sock = request_queue.get(timeout=1)
                try:
                    logging.info('Message received from connection {}. Msg: {}'.format(client_sock.getpeername(), msg))
                    client_sock.sendall(Worker._process_message(msg, open_filenames).encode('utf-8'))
                except InvalidRequest:
                    client_sock.sendall(b'{"error": "invalid request"}\n')
                except AppIdDoesNotExist:
                    client_sock.sendall(b'{"error": "app id does not exist"}\n')
                finally:
                    available_process_indices.put(worker_id)
                client_sock.close()
            except _queue.Empty:
                pass
        logging.debug(f'WORKER {worker_id} exiting gracefully')

    @staticmethod
    def _process_message(message_string, open_filenames):
        try:
            message_dict = json.loads(message_string)
        except json.decoder.JSONDecodeError:
            raise InvalidRequest
        if type(message_dict) is not dict:
            raise InvalidRequest
        if log := message_dict.get('log'):
            log_message(log, open_filenames)
            return "LOGGED: {}\n".format(message_string)
        elif query := message_dict.get('query'):
            return "RESULT: {}\n".format(search_logs(query, open_filenames))
        else:
            raise InvalidRequest

    @staticmethod
    def _set_sigterm_callback():
        signal.signal(signal.SIGTERM, do_nothing)
        signal.signal(signal.SIGINT, do_nothing)
