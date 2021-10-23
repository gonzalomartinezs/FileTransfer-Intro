import socket
import threading

class AtomicUDPSocket:
    def __init__(self, port: int = None):
        self.send_mutex = threading.Lock()
        self.sckt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if (port != None):
            self.sckt.bind(('127.0.0.1', port))

    def sendto(self, msg: bytes, addr: tuple[str, int]):
        self.send_mutex.acquire()
        self.sckt.sendto(msg, addr)
        self.send_mutex.release()

    def recvfrom(self, buff_size: int) -> tuple[bytes, tuple[str, int]]:
        return self.sckt.recvfrom(buff_size)

    def settimeout(self, timeout: float):
        self.sckt.settimeout(timeout)

    def close(self):
        self.send_mutex.acquire()
        self.sckt.close()
        self.send_mutex.release()
