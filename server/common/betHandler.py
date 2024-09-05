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
    return msg

def check_exit_msg(msg):
    if "EXIT" in msg[0:4]:
        return True
    return False

def parse_bets(msg, client_sock):
    bets = msg.split("\n")
    bets = [bet.rstrip('\r') for bet in bets]
    if bets[-1] == "":
        bets.pop()
    finalBets = []
    for bet in bets:
        new_bet = Bet(*bet.split(","))
        finalBets.append(new_bet)
    return finalBets


def confirm_upload_to_client(client_sock):
    client_sock.sendall("{}\n".format("1").encode('utf-8'))