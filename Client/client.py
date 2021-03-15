# Code for the client
##
import hashlib
import math
import socket
import traceback
from concurrent.futures import ThreadPoolExecutor
import time


host = '127.0.0.1'
port = 1233
BufferSize = 1024

File_path = "./data/media/"

SYN = 'Hello'
AKN = 'Ready'
AKN_NAME = 'Name'
AKN_OK = 'Ok'
AKN_HASH = 'HashOk'
ERROR = 'Error'
AKN_COMPLETE = 'SendComplete'


class ClientProtocol:

    def __init__(self):
        print('Waiting for connection')

        self.client_socket = socket.socket()

        try:
            self.client_socket.connect((host, port))
        except socket.error as e:
            print('Client Says: error creating socket ', str(e))

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

    def receive_from_server(self):
        return self.client_socket.recv(BufferSize).decode('utf-8')

    def send_to_server(self, segment, print_message):
        self.client_socket.send(str.encode(segment))
        print(print_message)

    def verify_reply(self, received, expected):
        if not expected == received:
            raise Exception("Error in protocol: expected {}; received {}".format(expected, received))

    def verify_reply_not_null(self, reply, expected):
        if not reply:
            raise Exception("Error in protocol: expected {}; received nothing".format(expected))

    def run(self):

        while True:

            try:
                self.send_to_server(SYN, "Client Says: Hail sent to server")

                reply = self.receive_from_server()

                self.verify_reply(reply, SYN)
                print("Client Says: Hail back from server")

                self.send_to_server(AKN, "Client Says: communicating to server that client is ready for file transport")

                reply = self.receive_from_server()

                self.verify_reply_not_null(reply, 'file name')

                file_name = reply

                self.send_to_server(AKN_NAME, "Client Says: file name received from server: {}".format(file_name))

                reply = self.receive_from_server()

                self.verify_reply_not_null(reply, 'file hash')

                serverHash = reply

                self.send_to_server(AKN_OK, "Client Says: file hash received from server: {}".format(serverHash))

                size = int(self.receive_from_server())
                print("Client Says: file size received from server: {}".format(size))

                with open(File_path + file_name, 'wb') as f:
                    print("Client Says: file created")

                    for _ in range(math.ceil(size / BufferSize)):
                        # read only 1024 bytes at a time
                        data = self.client_socket.recv(BufferSize)
                        print("Client Says: file chuck received from server: {}".format(data))
                        f.write(data)

                    f.close()
                    print("Client Says: file transmission is complete")

                calculated_hash = self.hash_file(file_name)
                is_valid = calculated_hash == serverHash

                if is_valid:

                    self.send_to_server(AKN_HASH, "File integrity is verified with calculated hash {}".format(calculated_hash))
                    self.client_socket.close()
                    break
                else:
                    self.send_to_server(ERROR,
                                        "File integrity could not be verified with calculated hash {}".format(calculated_hash))
                    break

            except Exception as err:
                self.client_socket.close()
                print("Client Says: Error during file transport with server")
                traceback.print_stack(err.__traceback__)
                break

def main():

    c = ClientProtocol()
    c.run()


if __name__ == "__main__":
    main()
