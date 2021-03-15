##
# Code for the server
import hashlib
import math
import socket
import threading
import traceback
from _thread import *

host = '127.0.0.1'
port = 1233
BufferSize = 1024

File_path = "data/media/"
Log_path = "data/logs/"
File_name = 'Test.mp4'
# open in binary

SYN = 'Hello'
AKN_READY = 'Ready'
AKN_NAME = 'Name'
AKN_OK = 'Ok'
AKN_HASH = 'HashOk'
AKN_COMPLETE = 'SendComplete'
ERROR = 'Error'


def threadsafe_function(fn):
    """decorator making sure that the decorated function is thread safe"""
    lock = threading.Lock()

    def new(*args, **kwargs):
        lock.acquire()
        try:
            r = fn(*args, **kwargs)
        except Exception as e:
            raise e
        finally:
            lock.release()
        return r

    return new


class ServerProtocol:

    def __init__(self, clients_number, file_number):

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.thread_count = 0
        self.clients_number = clients_number
        self.file_number = file_number
        self.ready_clients = 0
        self.all_ready_monitor = threading.Event()

        try:
            self.server_socket.bind((host, port))
        except socket.error as e:
            print(str(e))

        print('Waitiing for a Connection..')
        self.server_socket.listen(5)

    def send_file_to_client(self, connection, thread_id):
        while True:
            try:
                reply = self.receive_from_client(connection)
                self.verify_reply(reply, SYN)

                self.send_to_client(connection, SYN, "Server Says: Hail from client {} received".format(thread_id))

                reply = self.receive_from_client(connection)

                self.verify_reply(reply, AKN_READY)

                self.update_ready_clients()

                while not self.all_clients_ready(thread_id):
                    print('Server Says: client {} is put in wait for the rest of clients'.format(thread_id))
                    self.all_ready_monitor.wait()

                self.send_to_client(connection, File_name, "Server Says: Sending file name ({}) to client "
                                                           "{}".format(File_name, thread_id))

                reply = self.receive_from_client(connection)

                self.verify_reply(reply, AKN_NAME)

                hash = self.hash_file()
                self.send_to_client(connection, hash,
                                    "Server Says: Sending file hash ({}) to client {}".format(hash, thread_id))
                reply = self.receive_from_client(connection)

                self.verify_reply(reply, AKN_OK)

                size = str(self.get_file_size())

                self.send_to_client(connection, size,
                                    "Server Says: Sending file size ({}) to client {}".format(size, thread_id))
                self.send_file(connection, thread_id)

                reply = connection.recv(BufferSize).decode('utf-8')
                self.verify_reply(reply, AKN_HASH)
                print("Server Says: File integrity verified by  client {}".format(thread_id))

                connection.close()
                break

            except Exception as err:
                connection.close()
                print("Server Says: Error during file transmission to client {}".format(thread_id))
                traceback.print_stack(err.exc_info)
                break

    def receive_from_client(self, connection):
        return connection.recv(BufferSize).decode('utf-8')

    def send_to_client(self, connection, segment, print_message):
        connection.send(str.encode(segment))
        print(print_message)

    def verify_reply(self, received, expected):
        if not expected == received:
            raise Exception("Error in protocol: expected {}; received {}".format(expected, received))

    @threadsafe_function
    def all_clients_ready(self, thread_id):

        all_ready = self.clients_number - self.ready_clients == 0

        if all_ready:
            print("Server Says: all clients ready: starting file transport to client {}".format(thread_id))

        return all_ready

    def send_file(self, connection, thread_id):

        size = self.get_file_size()

        with open(File_path + File_name, 'rb') as file:
            for _ in range(math.ceil(size / BufferSize)):
                # read only 1024 bytes at a time
                chunk = file.read(BufferSize)
                connection.send(chunk)

            print("Server Says: File transmission is complete to client {}".format(thread_id))
            file.close()

    def get_file_size(self):
        with open(File_path + File_name, 'rb') as file:
            packed_file = file.read()
        return int(len(packed_file))

    def hash_file(self):
        file = open(File_path + File_name, 'rb')  # open in binary

        """"This function returns the SHA-1 hash
        of the file passed into it"""
        # make a hash object
        h = hashlib.sha1()

        # open file for reading in binary mode

        # loop till the end of the file
        chunk = 0
        while chunk != b'':
            # read only 1024 bytes at a time
            chunk = file.read(BufferSize)
            h.update(chunk)
        file.close()

        # return the hex representation of digest
        return h.hexdigest()

    def close(self):
        self.server_socket.close()

    @threadsafe_function
    def update_ready_clients(self):
        self.ready_clients += 1

        if self.clients_number - self.ready_clients == 0:
            self.all_ready_monitor.set()

    def run(self):

        while True:
            print('Listening at', self.server_socket.getsockname())

            Client, address = self.server_socket.accept()
            self.thread_count += 1

            print('Connected to: ' + address[0] + ':' + str(address[1]))

            if self.thread_count <= self.clients_number:
                start_new_thread(self.send_file_to_client, (Client, self.thread_count))

            print('Thread Number: ' + str(self.thread_count))


s = ServerProtocol(3, 1)
s.run()
