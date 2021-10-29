import socket
import threading
import random

from lib.general.constants import PACKET_LOSS_PROBABILITY

class AtomicUDPSocket:
    def __init__(self):
        self.send_mutex = threading.Lock()
        self.sckt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def bind(self, addr):
        self.sckt.bind(addr)

    def connect(self, addr):
        self.sckt.connect(addr)

    def sendto(self, msg: bytes, addr):
        self.send_mutex.acquire()
        try:
            if PACKET_LOSS_PROBABILITY <= random.randint(0, 100): # This lets us simulate packet loss
                self.sckt.sendto(msg, addr)
            self.send_mutex.release()
        # There was a Connection Error detected by the OS (or some other kind
        # of unknown error)
        except BaseException:
            self.send_mutex.release()
            raise ConnectionRefusedError

    def send(self, msg: bytes):
        self.send_mutex.acquire()
        try:
            self.sckt.send(msg)
            self.send_mutex.release()
        # There was a Connection Error detected by the OS (or some other kind
        # of unknown error)
        except BaseException:
            self.send_mutex.release()
            raise ConnectionRefusedError

    def recvfrom(self, buff_size: int):
        return self.sckt.recvfrom(buff_size)

    def recv(self, buff_size: int) -> bytes:
        return self.sckt.recv(buff_size)

    def settimeout(self, timeout: float):
        self.sckt.settimeout(timeout)

    def close(self):
        self.send_mutex.acquire()
        self.sckt.close()
        self.send_mutex.release()
