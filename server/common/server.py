import socket
import logging
import signal
import sys
from .utils import has_won, load_bets, store_bets, Bet

class Server:
    def __init__(self, port, listen_backlog, cantidad_clientes):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._cantidad_clientes = cantidad_clientes
        self._clients_uploading_bets = cantidad_clientes
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

    def __verify_winners(self,id):
        bets = load_bets()
        winners = [bet for bet in bets if has_won(bet)]
        self.winners = winners
        logging.info(
            f'action: set_winners_from_store | result: success | winners: {len(winners)}')
        winners = [bet for bet in winners if bet.agency == int(id)]

        return winners

    def __handle_down_bet(self, id, client_sock):
        """
        Handles a down bet message

        This method should parse the message and store the bet
        """
        id = int(id)
        if self._clients_uploading_bets > 0:
            self._clients_uploading_bets -= 1
        if self._clients_uploading_bets == 0:
            winners = self.__verify_winners(id)
            str_winners = [bet.document for bet in winners]
            str_winners = ','.join(str_winners)
            client_sock.sendall("{}\n".format(str_winners).encode('utf-8'))

        else:
            client_sock.sendall("{}\n".format("FALTA").encode('utf-8'))

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        self._client_sockets.append(client_sock)
        
        try:
            # TODO: Modify the receive to avoid short-reads
            while True:
                msg = b""
                while True:
                    part = client_sock.recv(1024)
                    if not part:
                        break
                    msg += part
                    if b'\x00' in part:
                        msg = msg.rstrip(b'\x00')
                        break
                msg = msg.decode('utf-8')
                if msg == "exit":
                    break
                if "DOWN" in msg[0:4]:
                    self.__handle_down_bet(msg[4],client_sock)
                elif "UP" in msg[0:2]:
                    msg = msg[2:]
                    bets = msg.split("\n")
                    bets = [bet.rstrip('\r') for bet in bets]
                    if bets[-1] == "":
                        bets.pop()
                    addr = client_sock.getpeername()
                    logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
                    finalBets = []
                    for bet in bets:
                        new_bet = Bet(*bet.split(","))
                        finalBets.append(new_bet)
                    store_bets(finalBets)
                    logging.info(f'action: apuesta_recibida | result: success | cantidad: {len(finalBets)}')
                    client_sock.sendall("{}\n".format("1").encode('utf-8'))
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