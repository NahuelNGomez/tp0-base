from .utils import Bet, has_won, load_bets
from .const import DOWN, EXIT, UP


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

def parse_bets(msg):
    msg = msg[2:]
    bets = msg.split("\n")
    bets = [bet.rstrip('\r') for bet in bets]
    if bets[-1] == "":
        bets.pop()
    finalBets = []
    for bet in bets:
        new_bet = Bet(*bet.split(","))
        finalBets.append(new_bet)

    return finalBets

def check_type_msg(msg):
    if "EXIT" in msg[0:4]:
        return EXIT
    if "DOWN" in msg[0:4]:
        return DOWN
    elif "UP" in msg[0:2]:
        return UP
    else:
        return "UNKNOWN"
    
def confirm_upload_to_client(client_sock):
    client_sock.sendall("{}\n".format("1").encode('utf-8'))

    
def send_winners(client_sock, msg):
    id = get_id_down_msg(msg)
    winners = verify_winners(id)
    str_winners = [bet.document for bet in winners]
    str_winners = ','.join(str_winners)
    client_sock.sendall("{}\n".format(str_winners).encode('utf-8'))
    return len(winners)

def verify_winners(id):
    bets = load_bets()
    winners = [bet for bet in bets if has_won(bet)]
    winners = [bet for bet in winners if bet.agency == int(id)]
    return winners

def get_id_down_msg(msg):
    id = msg[4]
    return int(id)

def send_wait(client_sock):
    client_sock.sendall("{}\n".format("FALTA").encode('utf-8'))