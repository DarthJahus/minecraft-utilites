import threading
import time
from rcon.source import Client

# Configuration RCON
HOST = "127.0.0.1"
PORT = 65535
PASSWORD = "SicretRCONpassword"
TIMEOUT = 2  # RCON (sometimes, RCON hangs)
DELAY_TELEPORT = 5  # Teleportation delay

# World dimensions
CENTER_X = -0
CENTER_Z = -512
RADIUS = 4192//2
MARGIN = 128
STEP = 256
LEVEL_Y = 200

# Limits with margin
MIN_X = CENTER_X - (RADIUS - MARGIN)
MAX_X = CENTER_X + (RADIUS - MARGIN)
MIN_Z = CENTER_Z - (RADIUS - MARGIN)
MAX_Z = CENTER_Z + (RADIUS - MARGIN)

# Name of the player to teleport around
PLAYER = 'Admin'

def run_rcon_command(cmd):
    result = []
    
    def target():
        try:
            with Client(HOST, PORT, passwd=PASSWORD) as client:
                res = client.run(*cmd)
                result.append(res)
        except Exception as e:
            result.append(f"Erreur: {e}")
    
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout=TIMEOUT)
    
    if thread.is_alive():
        print(f"[TIMEOUT] Commande bloquée : {cmd}")
        return None
    else:
        print(f"> {cmd[0]}: {result[0]}")
        return result[0]


def generate_chunks_v():
    x = MAX_X
    go_down = True

    while x >= MIN_X:
        if go_down:
            z_range = range(MIN_Z, MAX_Z + 1, STEP)
        else:
            z_range = range(MAX_Z, MIN_Z - 1, -STEP)

        for z in z_range:
            cmd = ["tp", PLAYER, str(x), LEVEL_Y, str(z)]
            run_rcon_command(cmd)
            time.sleep(DELAY_TELEPORT)

        x -= STEP
        go_down = not go_down


def generate_chunks_h():
    z = MIN_Z
    go_right = False

    while z <= MAX_Z:
        if go_right:
            x_range = range(MIN_X, MAX_X + 1, STEP)
        else:
            x_range = range(MAX_X, MIN_X - 1, -STEP)

        for x in x_range:
            cmd = ["tp", PLAYER, str(x), LEVEL_Y, str(z)]
            run_rcon_command(cmd)
            time.sleep(DELAY_TELEPORT)

        z += STEP
        go_right = not go_right


if __name__ == "__main__":
    generate_chunks_v()
