# Code for the client
##
import hashlib
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

print('Waiting for connection')





def hash_file(file):
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

    # return the hex representation of digest
    return h.hexdigest()



try:
    ClientSocket.connect((host, port))
except socket.error as e:
    print(str(e))

Response = ClientSocket.recv(BufferSize)
while True:

    try:
        ClientSocket.send(str.encode(SYN))
        Response = ClientSocket.recv(BufferSize)

        file_name = ''

        if Response == SYN:
            print("Client Says: Hail back from server")

            ClientSocket.send(str.encode(AKN))

            Response = ClientSocket.recv(BufferSize).decode('utf-8')

        else:
            ClientSocket.send(str.encode(ERROR))

        if Response:

            print("Client Says: file name received from server")
            file_name = Response
            ClientSocket.send(str.encode(AKN_NAME))

            Response = ClientSocket.recv(BufferSize).decode('utf-8')

            if Response:

                print("Client Says: file hash received from server")
                serverHash = Response
                ClientSocket.send(str.encode(AKN_OK))


                with open(File_path + file_name, 'wb') as f:
                    print("Client Says: file opened")
                    while True:

                        data = ClientSocket.recv(BufferSize)
                        print("Client Says: file chuck received from server: {}".format(data))
                        if not data:
                            f.close()
                            print("Client Says: file data stream is complete")
                            break
                        # write data to a file
                        f.write(data)


                isValid = hash_file(f) == serverHash

                if isValid:
                    ClientSocket.send(str.encode(AKN_HASH))

    except Exception as err:
        ClientSocket.close()
        print("Client Says: Error during connection with server")
        traceback.print_tb(err.__traceback__)

    ClientSocket.close()


