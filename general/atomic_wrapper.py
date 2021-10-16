import threading

class AtomicWrapper:
    def __init__(self, data: any):
        self.mutex = threading.Lock()
        self.data = data

    def assign(self, data: any):
        self.mutex.acquire()
        self.data = data
        self.mutex.release()

    def read(self) -> any:
        ret = None
        self.mutex.acquire()
        ret = self.data
        self.mutex.release()
        return ret