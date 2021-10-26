import threading


class AcceptedConnections:
    def __init__(self):
        self.mutex = threading.Lock()
        self.accepted_connections = set()

    def add_connection(self, addr: tuple[str, int]):
        self.mutex.acquire()
        self.accepted_connections.add(addr)
        self.mutex.release()

    def remove_connection(self, addr: tuple[str, int]):
        self.mutex.acquire()
        self.accepted_connections.remove(addr)
        self.mutex.release()

    def __contains__(self, addr: tuple[str, int]):
        self.mutex.acquire()
        r = addr in self.accepted_connections
        self.mutex.release()
        return r
