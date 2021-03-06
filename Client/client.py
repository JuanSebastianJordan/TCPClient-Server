# Code for the client

import socket

ClientSocket = socket.socket()
host = '127.0.0.1'
port = 1233

print('Waiting for connection')
try:
    ClientSocket.connect((host, port))
except socket.error as e:
    print(str(e))

Response = ClientSocket.recv(1024)
while True:
    Input = input('File to transfer(fileA.txt or file.B.txt)/Exit: ')
    if Input=='Exit':
        break
    clients = input('How many clients?/Exit: ')
    if clients == 'Exit':
        break
    
    ClientSocket.send(str.encode(Input))
    Response = ClientSocket.recv(1024)
    print(Response.decode('utf-8'))

ClientSocket.close()