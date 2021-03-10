# Code for the client
##
import hashlib
import math
import socket
import traceback

ClientSocket = socket.socket()
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

print('Waiting for connection')





def hash_file():
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



try:
    ClientSocket.connect((host, port))
except socket.error as e:
    print(str(e))

while True:

    try:
        ClientSocket.send(str.encode(SYN))
        Response = ClientSocket.recv(BufferSize).decode('utf-8')

        if Response == SYN:
            print("Client Says: Hail back from server")

            ClientSocket.send(str.encode(AKN))
        else:
            print("Client Says: Error in protocol with server: {}".format(Response))
            ClientSocket.send(str.encode(ERROR))

        Response = ClientSocket.recv(BufferSize).decode('utf-8')

        if Response:

            file_name = Response
            print("Client Says: file name received from server: {}".format(file_name))
            ClientSocket.send(str.encode(AKN_NAME))

            Response = ClientSocket.recv(BufferSize).decode('utf-8')
            if Response:
                serverHash = Response
                print("Client Says: file hash received from server: {}".format(serverHash))
                ClientSocket.send(str.encode(AKN_OK))

                size = int(ClientSocket.recv(BufferSize).decode('utf-8'))
                print("Client Says: file size received from server: {}".format(size))

                with open(File_path + file_name, 'wb') as f:
                    print("Client Says: file created")

                    for _ in range(math.ceil(size / BufferSize)):
                        # read only 1024 bytes at a time
                        data = ClientSocket.recv(BufferSize)
                        # print("Client Says: file chuck received from server: {}".format(data))
                        f.write(data)


                    f.close()
                    print("Client Says: file data stream is complete")
                    print('askjdbjkbdkj')

                isValid = hash_file() == serverHash
                print(isValid)

                if isValid:
                    ClientSocket.send(str.encode(AKN_HASH))
                    ClientSocket.close()
                else:
                    ClientSocket.send(str.encode(ERROR))
    except Exception as err:
        ClientSocket.close()
        print("Client Says: Error during connection with server")
        traceback.print_stack(err.__traceback__)
        break

    ClientSocket.close()


