
##
import hashlib
import os

BufferSize = 1024

File_path = "/data/media/"
Log_path = "/data/logs/"
File_name = 'Test.mp4'


file = open(os.getcwd() + File_path + File_name, 'rb')  # open in binary

while True:
    l = file.read(BufferSize)
    print(l)
    while l:
        print("Server Says: Sent file chunk {} to  client {}".format(l, 8))

        l = file.read(BufferSize)
    if not l:
        file.close()
        break

file = open(os.getcwd() + File_path + File_name, 'rb')  # open in binary
""""This function returns the SHA-1 hash
of the file passed into it"""
# make a hash object
h = hashlib.sha1()

# open file for reading in binary mode

# loop till the end of the file
chunk = 0

while chunk != b'':
    print(chunk)
    # read only 1024 bytes at a time
    chunk = file.read(BufferSize)
    h.update(chunk)

# return the hex representation of digest



