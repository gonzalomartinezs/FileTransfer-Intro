import threading
from lib.general.client_thread import ClientThread


class ClientsAcceptor(threading.Thread):
    def __init__(self, sv_socket, arguments):
        threading.Thread.__init__(self)
        self.socket = sv_socket
        self.clients = []
        self.keep_running = True
        self.args = arguments

    def run(self):
        while self.keep_running == True:
            try:
                self.__release_dead_clients()

                peer = self.socket.accept()
                client_thread = ClientThread(peer, self.args)
                self.clients.append(client_thread)
                self.clients[-1].start()

            except BaseException:
                pass

    def stop(self):
        self.keep_running = False

    def __release_dead_clients(self):
        for client in self.clients:
            if client.is_dead():
                client.join()
                self.clients.remove(client)

    def __del__(self):
        for client in self.clients:
            client.stop()
            client.join()
