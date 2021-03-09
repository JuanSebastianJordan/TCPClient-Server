##
#Code for the server
import socket
import os
from _thread import *

host = '127.0.0.1'
port = 1233
ThreadCount = 0


File_path = "./data/media/"
Log_path = "./data/logs/"
File_name = ''
File = open(File_path + File_name,'wb') #open in binary

SYN = 'Hello'
AKN = 'Ready'
AKN_NAME = 'Name'

ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waitiing for a Connection..')
ServerSocket.listen(5)



def threaded_client(connection):
    connection.send(str.encode('Welcome to the Server'))
    while True:

        reply = connection.recv(1024).decode('utf-8')
        if reply == SYN:
            print("Server Says: Hail from client received");

            connection.sendall(str.encode(reply))
            reply = connection.recv(1024).decode('utf-8')

            if reply == AKN:
                print("Server Says: Sending file name to client " + File_name)
                connection.sendall(str.encode(File_name))
                reply = connection.recv(1024).decode('utf-8')

                if reply == AKN_NAME :
                    pass

        else :
            print("Server Says: : Unable to connect to client");
            connection.close()

        while True:
            l = File.read(1024)
            while (l):
                connection.send(l)
                # print('Sent ',repr(l))
                l = File.read(1024)
            if not l:
                File.close()
                break

        print(reply)
        connection.sendall(str.encode(reply))
    connection.close()

def close():
    ServerSocket.close()

while True:
    print ('Listening at', ServerSocket.getsockname())
    Client, address = ServerSocket.accept()

    print('Connected to: ' + address[0] + ':' + str(address[1]))

    start_new_thread(threaded_client, (Client, ))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))
   


    