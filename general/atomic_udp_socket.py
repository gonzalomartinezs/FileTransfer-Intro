import socket
import threading


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
        self.sckt.sendto(msg, addr)
        self.send_mutex.release()

    def send(self, msg: bytes):
        self.send_mutex.acquire()
        self.sckt.send(msg)
        self.send_mutex.release()

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
