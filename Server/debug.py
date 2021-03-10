
##
import hashlib
import os

BufferSize = 1024

File_path = "data/media/"
Log_path = "data/logs/"
File_name = 'f.mp4'

with open(File_path + File_name, 'rb') as file: # open in binary

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
        print(chunk)
        h.update(chunk)

    # return the hex representation of digest
    print(h.hexdigest())
