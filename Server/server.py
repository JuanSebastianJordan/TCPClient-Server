##
# Code for the server
import hashlib
import math
import socket
import os
import traceback
from _thread import *

host = '127.0.0.1'
port = 1233
ThreadCount = 0
BufferSize = 1024

File_path = "data/media/"
Log_path = "data/logs/"
File_name = 'Test.mp4'
 # open in binary

SYN = 'Hello'
AKN = 'Ready'
AKN_NAME = 'Name'
AKN_OK = 'Ok'
AKN_HASH = 'HashOk'
AKN_COMPLETE = 'SendComplete'
ERROR = 'Error'

ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waitiing for a Connection..')
ServerSocket.listen(5)


def threaded_client(connection, idThread):
    while True:

        try:
            reply = connection.recv(BufferSize).decode('utf-8')
            if reply == SYN:
                print("Server Says: Hail from client {} received".format(idThread))
                connection.send(str.encode(SYN))

                reply = connection.recv(BufferSize).decode('utf-8')

                if reply == AKN:


                    print("Server Says: Sending file name ({}) to client {}".format(File_name, idThread))
                    connection.send(str.encode(File_name))
                    reply = connection.recv(BufferSize).decode('utf-8')

                    if reply == AKN_NAME:
                        hash = hash_file()
                        print("Server Says: Sending file hash ({}) to client {}".format(hash, idThread))
                        connection.send(str.encode(hash))

                        reply = connection.recv(BufferSize).decode('utf-8')
                        if reply == AKN_OK:
                            print('sending file')

                            size = get_file_size()
                            connection.send(str.encode(str(size)))
                            print("Server Says: Sending file size ({}) to client {}".format(size, idThread))
                            send_file(connection, idThread)

                            reply = connection.recv(BufferSize).decode('utf-8')
                            if reply == AKN_HASH:
                                print("Server Says: File successfully sent to client {}".format(hash))
                                connection.close()
                                break


            print("Server Says: Unable to connect to client {}".format(idThread))
            connection.close()

        except Exception as err:
            connection.close()
            print("Server Says: Error during connection with client {}".format(idThread))
            traceback.print_stack(err.__traceback__)
            break


def send_file(connection, idThread):

    size = get_file_size()

    with open(File_path + File_name, 'rb') as file:
        chunk = 0
        for _ in range(math.ceil(size / BufferSize)):
            # read only 1024 bytes at a time
            chunk = file.read(BufferSize)

            print("Server Says: Sent file chunk {} to  client {}".format(chunk, idThread))
            connection.send(chunk)


        print("Server Says: File transmission is complete")
        file.close()


def get_file_size():
    with open(File_path + File_name, 'rb') as file:
        packed_file = file.read()
    return int(len(packed_file))

def hash_file():
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


def close():
    ServerSocket.close()


while True:
    print('Listening at', ServerSocket.getsockname())

    Client, address = ServerSocket.accept()

    print('Connected to: ' + address[0] + ':' + str(address[1]))

    start_new_thread(threaded_client, (Client, ThreadCount))

    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))
