import socket
import logging
import signal
import sys

from .betHandler import confirm_upload_to_client, parse_bet, recieve_msg
from .utils import store_bets, Bet

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._client_sockets = []

        signal.signal(signal.SIGTERM, self._graceful_shutdown)

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        while True:
            client_sock = self.__accept_new_connection()
            self.__handle_client_connection(client_sock)

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        self._client_sockets.append(client_sock)
        
        try:

            msg = recieve_msg(client_sock)
            bet = parse_bet(msg)
            addr = client_sock.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
            store_bets(bet)
            logging.info(f'action: apuesta_almacenada | result: success | dni: {bet[0].document} | numero: {bet[0].number}')
            confirm_upload_to_client(client_sock)
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.close()
            self._client_sockets.remove(client_sock)

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c

    def _graceful_shutdown(self, signum, frame):
        """
        Maneja el cierre del servidor de manera ordenada.

        Este método se ejecutará cuando se reciba una señal SIGTERM.
        """
        logging.info(f"action: signal_received | signal: {signum} | result: graceful_shutdown_initiated")

        if self._server_socket:
            self._server_socket.close()
            logging.info("action: close_server_socket | result: success")
        

        for client_sock in self._client_sockets:
            try:
                client_sock.close()
                logging.info("action: close_client_socket | result: success")
            except OSError as e:
                logging.error(f"action: close_client_socket | result: fail | error: {e}")

        logging.info("action: cleanup_resources | result: success")
        sys.exit(0)