# Code for the client
##
import hashlib
import logging
import math
import socket
import sys
import threading
import time
from tqdm import tqdm
from datetime import datetime
from threading import Thread

# host = '54.162.149.119'
host = 'localhost'
port = 60002
# port = 60002
BUFFER_SIZE = 1024

File_path = "ArchivosRecibidos/"

SYN = 'Hello'
AKN_READY = 'Ready'
AKN_NAME = 'Name'
AKN_OK = 'Ok'
AKN_HASH = 'HashOk'
ERROR = 'Error'
AKN_COMPLETE = 'SendComplete'



class ClientProtocol:

    def __init__(self):
        self.id = 0
        self.clients_number = 0
        self.server_file_name = ''
        self.client_file_name = ''
        self.file_size = 0
        self.running_time = 0
        self.success_connection = True
        self.packages_received = 0
        self.bytes_received = 0
        self.log_info = ''
        self.port = ''
        self.ip = ''

        print('Client thread started')

    def hash_file(self, file_name):
        with open(File_path + file_name, 'rb') as file:
            """"This function returns the SHA-1 hash
            of the file passed into it"""
            # make a hash object
            h = hashlib.sha1()

            # open file for reading in binary mode

            # loop till the end of the file
            chunk = 0
            while chunk != b'':
                # read only 1024 bytes at a time
                chunk = file.read(BUFFER_SIZE)
                h.update(chunk)
            file.close()

        # return the hex representation of digest
        return h.hexdigest()

    def receive_from_server(self, client_socket):
        B = client_socket.recv(BUFFER_SIZE)
        b = B.decode('utf-8')
        self.bytes_received += len(B)
        self.packages_received += 1
        return b

    def send_to_server(self, client_socket, segment, print_message):
        b = client_socket.send(str.encode(segment))

        print("\n", print_message)

    def verify_reply(self, received, expected):
        if not expected == received:
            raise Exception("Error in protocol: expected {}; received {}".format(expected, received))

    def verify_reply_not_null(self, reply, expected):
        if not reply:
            raise Exception("Error in protocol: expected {}; received nothing".format(expected))

    def run(self):

        print('Waiting for connection')

        client_socket = socket.socket()

        try:
            client_socket.connect((host, port))
            self.port = client_socket.getsockname()[1]
            self.ip = socket.gethostname()
        except socket.error as e:
            print('Client{} Says: error creating socket ', str(e))

        while True:

            try:
                self.send_to_server(client_socket, SYN, "Client Says: Hail sent to server")

                reply = self.receive_from_server(client_socket)
                self.verify_reply(reply, SYN)
                print("Client Says: Hail back from server")

                reply = self.receive_from_server(client_socket)
                self.verify_reply_not_null(reply, 'client id')

                self.id = int(reply.split(';')[0])
                self.clients_number = int(reply.split(';')[1])

                print("Client Says: id {} received from server".format(self.id))

                self.send_to_server(client_socket, AKN_READY,
                                    "Client Says: communicating to server that client is ready for file transport")




                reply = self.receive_from_server(client_socket)

                self.verify_reply_not_null(reply, 'file name')

                self.server_file_name = reply

                self.send_to_server(client_socket, AKN_NAME,
                                    "Client{} Says: file name received from server: {}".format(self.id,
                                                                                               self.server_file_name))

                reply = self.receive_from_server(client_socket)

                self.verify_reply_not_null(reply, 'file hash')

                serverHash = reply

                self.send_to_server(client_socket, AKN_OK,
                                    "Client{} Says: file hash received from server: {}".format(self.id, serverHash))

                self.file_size = int(self.receive_from_server(client_socket))
                print("Client{} Says: file size received from server: {}".format(self.id, self.file_size))

                self.client_file_name = "Cliente{}-Prueba-{}.{}".format(self.id, self.clients_number,
                                                                        self.server_file_name.split('.')[-1])

                start_time = time.time()

                progress = tqdm(range(self.file_size), f" Client{self.id} receiving {self.server_file_name}", unit="B",
                                unit_scale=True,
                                unit_divisor=BUFFER_SIZE)
                with open(File_path + self.client_file_name, "wb") as f:

                    bytes_read = b''
                    complete = False
                    while not complete:
                        # read 1024 bytes from the socket (receive)

                        # update the progress bar
                        progress.update(len(bytes_read))
                        # write to the file the bytes we just received
                        f.write(bytes_read)
                        bytes_read = client_socket.recv(BUFFER_SIZE)
                        complete = int.from_bytes(str.encode(AKN_COMPLETE), "big") == int.from_bytes(bytes_read, "big")

                        self.bytes_received += len(bytes_read)
                        self.packages_received += 1
                        # print("Client{} Says: file chuck received from server: {}".format(self.id, data))

                    f.close()

                self.send_to_server(client_socket, AKN_COMPLETE,
                                    "Client{} Says: file transmission is complete".format(self.id))

                self.running_time = time.time() - start_time

                calculated_hash = self.hash_file(self.client_file_name)
                is_valid = calculated_hash == serverHash

                if is_valid:

                    self.send_to_server(client_socket, AKN_HASH,
                                        "File integrity is verified with calculated hash {}".format(calculated_hash))
                    client_socket.close()

                    self.log_info_c()
                    break
                else:
                    self.send_to_server(client_socket, ERROR,
                                        "File integrity could not be verified with calculated hash {}".format(
                                            calculated_hash))
                    self.log_info_c()
                    break


            except Exception as err:
                client_socket.close()
                print("Client{} Says: Error during file transport with server: {}".format(self.id, str(err)))
                self.success_connection = True
                self.log_info_c()
                break

    def log_info_c(self):
        logging.info(
            '_____________________________________________________________________________________________________')
        d = {1: 'yes', 2: 'no'}
        logging.info('Client{}: File name: {}'.format(self.id, self.server_file_name))
        logging.info('Client{}: File size: {}'.format(self.id, self.file_size))
        logging.info('Client{}: Client connection: ({}:{})'.format(self.id, self.ip, self.port))
        logging.info('Client{}: Successful: {}'.format(self.id, d[self.success_connection]))
        logging.info('Client{}: Running time: {} s'.format(self.id, self.running_time))
        logging.info('Client{}: Bytes received: {} B'.format(self.id, self.bytes_received))
        logging.info('Client{}: Packages received {}'.format(self.id, self.packages_received))



def main():
    c = ClientProtocol()
    c.run()


if __name__ == "__main__":
    main()
