import socket
import logging
import signal
import sys

from .betHandler import check_type_msg, confirm_upload_to_client, parse_bets, recieve_msg, send_wait, send_winners

from .const import DOWN, EXIT, UP
from .utils import has_won, load_bets, store_bets, Bet

class Server:
    def __init__(self, port, listen_backlog, cantidad_clientes):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._cantidad_clientes = cantidad_clientes
        self._clients_uploading_bets = list(range(1, cantidad_clientes + 1)) # Clients that are uploading bets. Starts with all clients
        self._client_sockets = []

        signal.signal(signal.SIGTERM, self._graceful_shutdown)

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        # TODO: Modify this program to handle signal to graceful shutdown
        # the server
        while True:
            client_sock = self.__accept_new_connection()
            self.__handle_client_connection(client_sock)

    def __handle_down_bet(self, msg, client_sock):
        """
        Handles a down bet message

        This method should parse the message and store the bet
        """

        if self._clients_uploading_bets == []:
            amount_winners = send_winners(client_sock, msg)
            logging.info(
            f'action: piden_resultados | result: success | winners: {amount_winners}')
        else:
            logging.info(
            f'action: piden_resultados | result: fail')
            send_wait(client_sock)
    
    def __handle_up_bet(self, msg, client_sock):
        bets = parse_bets(msg)

        store_bets(bets)
        logging.info(f'action: apuesta_recibida | result: success | cantidad: {len(bets)}')
        confirm_upload_to_client(client_sock)

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        self._client_sockets.append(client_sock)
        
        try:
            while True:
                msg = recieve_msg(client_sock)
                type = check_type_msg(msg)
                if type == EXIT:
                    self._clients_uploading_bets.remove(int(msg[4]))
                    if self._clients_uploading_bets == []:
                        logging.info(f'action: sorteo | result: success')
                    break
                elif type == DOWN:
                    self.__handle_down_bet(msg,client_sock)
                    break
                elif type == UP:
                    self.__handle_up_bet(msg,client_sock)
                    
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