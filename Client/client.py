# Code for the client
##
import hashlib
import math
import socket
import traceback
from _thread import start_new_thread
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

host = '127.0.0.1'
port = 1233
BufferSize = 1024

File_path = "ArchivosRecibidos/"

SYN = 'Hello'
AKN = 'Ready'
AKN_NAME = 'Name'
AKN_OK = 'Ok'
AKN_HASH = 'HashOk'
ERROR = 'Error'
AKN_COMPLETE = 'SendComplete'


class ClientProtocol(Thread):

    def __init__(self, id, clients_number):
        Thread.__init__(self)
        self.id = id
        self.clients_number = clients_number
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
                chunk = file.read(BufferSize)
                h.update(chunk)
            file.close()

        # return the hex representation of digest
        return h.hexdigest()

    def receive_from_server(self, client_socket):
        return client_socket.recv(BufferSize).decode('utf-8')

    def send_to_server(self, client_socket, segment, print_message):
        client_socket.send(str.encode(segment))
        print(print_message)

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
        except socket.error as e:
            print('Client{} Says: error creating socket ', str(e))

        while True:

            try:
                self.send_to_server(client_socket, SYN, "Client{} Says: Hail sent to server".format(self.id))

                reply = self.receive_from_server(client_socket)

                self.verify_reply(reply, SYN)
                print("Client{} Says: Hail back from server".format(self.id))

                self.send_to_server(client_socket, AKN,
                                    "Client{} Says: communicating to server that client is ready for file transport".format(self.id))

                reply = self.receive_from_server(client_socket)

                self.verify_reply_not_null(reply, 'file name')

                file_name = reply

                self.send_to_server(client_socket, AKN_NAME,
                                    "Client{} Says: file name received from server: {}".format(self.id, file_name))

                reply = self.receive_from_server(client_socket)

                self.verify_reply_not_null(reply, 'file hash')

                serverHash = reply

                self.send_to_server(client_socket, AKN_OK,
                                    "Client{} Says: file hash received from server: {}".format(self.id, serverHash))

                size = int(self.receive_from_server(client_socket))
                print("Client{} Says: file size received from server: {}".format(self.id, size))

                name = "Cliente{}-Prueba-{}-{}".format(self.id, self.clients_number, file_name)
                with open(File_path + name
                        , 'wb') as f:
                    print("Client{} Says: file created")

                    for _ in range(math.ceil(size / BufferSize)):
                        # read only 1024 bytes at a time
                        data = client_socket.recv(BufferSize)
                        # print("Client{} Says: file chuck received from server: {}".format(self.id, data))
                        f.write(data)

                    f.close()
                    print("Client{} Says: file transmission is complete")

                calculated_hash = self.hash_file(file_name)
                is_valid = calculated_hash == serverHash

                if is_valid:

                    self.send_to_server(client_socket, AKN_HASH,
                                        "File integrity is verified with calculated hash {}".format(calculated_hash))
                    client_socket.close()
                    break
                else:
                    self.send_to_server(client_socket, ERROR,
                                        "File integrity could not be verified with calculated hash {}".format(
                                            calculated_hash))
                    break

            except Exception as err:
                client_socket.close()
                print("Client{} Says: Error during file transport with server: {}".format(self.id, str(err)))

                break


def main():
    cn = int(input("Indicate number of clients to connect to server \n"))
    for n in range(cn):
        c = ClientProtocol(n + 1, cn)
        c.start()


if __name__ == "__main__":
    main()
