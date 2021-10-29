import threading
import os
from lib.general.constants import *
from lib.general import file_finder
from lib.general.file_reader import FileReader


class ClientThread(threading.Thread):
    def __init__(self, peer, arguments):
        threading.Thread.__init__(self)
        self.peer = peer[0]
        self.keep_running = True
        self.storage = arguments.storage
        self.verbose = arguments.verbose
        self.quiet = arguments.quiet

    def run(self):
        while self.keep_running:
            received = self.peer.recv(MAX_BUFFER_SIZE)
            command, name, size = received.decode().split(',')
            filepath = os.path.join(self.storage, name)

            if int(command) == 0:
                self.__recv_file(name, filepath, size)
            else:
                self.__send_file(name, filepath)

            self.keep_running = False
            self.peer.close()

    def stop(self):
        self.keep_running = False

    def is_dead(self):
        return self.keep_running == False

    def __recv_file(self, name, filepath, size):
        file_exists = file_finder.file_exists(self.storage, name)
        if file_exists:
            message = "1"
        else:
            message = "0"
        self.peer.sendall(message.encode())

        if file_exists:
            end_exchange = self.peer.recv(MAX_BUFFER_SIZE)
            if int(end_exchange.decode()) == 1:  # No desea sobreescribirlo
                return

        file = open(filepath, "wb")
        print("Saving " + name + " in " + self.storage)

        received = self.peer.recv(MAX_BUFFER_SIZE)
        bytes_received = len(received)
        while received != b'' and bytes_received <= int(size):
            file.write(received)
            if bytes_received == int(size):
                break # This avoids waiting for more time in the recv that has an already closed connection
            received = self.peer.recv(MAX_BUFFER_SIZE)
            bytes_received += len(received)

        if bytes_received == int(size):
            print(name + " was successfully uploaded.")
        else:
            print(name + "is corrupted, unknown error.")
        file.close()

    def __send_file(self, name, filepath):
        file_exists = file_finder.file_exists(self.storage, name)
        if not file_exists:
            message = "0"
        else:
            message = str(os.path.getsize(filepath))

        self.peer.sendall(message.encode())

        if file_exists:
            try:
                file = FileReader(filepath)
            except IOError:
                print("Unable to open file " + filepath + ".")
            else:
                bytes_sent = 0
                continue_reading = True
                while continue_reading:
                    try:
                        bytes_read = file.read_next_section(MAX_BUFFER_SIZE)
                        self.peer.sendall(bytes_read)
                        bytes_sent += len(bytes_read)
                    except EOFError:
                        continue_reading = False
                        if bytes_sent == os.path.getsize(filepath):
                            print(name + " successfully sent.")
                        else:
                            print("An error occurred while sending the file."
                                  "Some bytes were not delivered.")
                    except BaseException:
                        continue_reading = False
                        print("An error occurred while sending the file.")
                file.close()
