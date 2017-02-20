import socket
import logging


def is_connection_valid(ip, port):
    s = socket.socket()

    try:
        s.connect((ip, port))
        s.close()
        return True
    except socket.error as e:
        logging.error(e)
        return False

