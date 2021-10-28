import threading
import os
import general.shared_constants as constants
import general.file_finder as file_finder
from general.file_reader import FileReader


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
            received = self.peer.recv(constants.MAX_BUFFER_SIZE)
            command, name = received.decode().split(',')
            filepath = os.path.join(self.storage, name)

            if int(command) == 0:
                self.__recv_file(name, filepath)
            else:
                self.__send_file(name, filepath)

            self.keep_running = False
            self.peer.close()

    def stop(self):
        self.keep_running = False

    def is_dead(self):
        return self.keep_running == False

    def __recv_file(self, name, filepath):
        file_exists = file_finder.file_exists(self.storage, name)
        if file_exists:
            message = "1"
        else:
            message = "0"
        self.peer.send(message.encode())

        if file_exists:
            end_exchange = self.peer.recv(constants.MAX_BUFFER_SIZE)
            if int(end_exchange.decode()) == 1:  # No desea sobreescribirlo
                return

        file = open(filepath, "wb")
        print("Saving " + name + " in " + self.storage)

        received = self.peer.recv(constants.MAX_BUFFER_SIZE)
        while received != b'':
            file.write(received)
            received = self.peer.recv(constants.MAX_BUFFER_SIZE)

        print(name + " was successfully uploaded.")
        file.close()

    def __send_file(self, name, filepath):
        file_exists = file_finder.file_exists(self.storage, name)
        if not file_exists:
            message = "1"
        else:
            message = "0"
        self.peer.send(message.encode())

        if file_exists:
            try:
                file = FileReader(filepath)
            except IOError:
                print("Unable to open file " + filepath + ".")
            else:
                continue_reading = True
                while continue_reading:
                    try:
                        bytes_read = file.read_next_section(constants.MAX_BUFFER_SIZE)
                        self.peer.send(bytes_read)
                    except EOFError:
                        continue_reading = False
                        print("File successfully sent.")
                    except BaseException:
                        continue_reading = False
                        print("An error occurred while sending the file.")
                file.close()
