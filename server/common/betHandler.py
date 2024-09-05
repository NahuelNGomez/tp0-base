from .utils import Bet


def recieve_msg(client_sock):
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
    msg = msg[:-1]      # Elimino el caracter nulo 0x00
    return msg

def parse_bet(msg):
    bets = msg.split("\n")
    finalBets = []
    for bet in bets:
        new_bet = Bet(*bet.split(","))
        finalBets.append(new_bet)
    return finalBets


def confirm_upload_to_client(client_sock):
    client_sock.sendall("{}\n".format("1").encode('utf-8'))