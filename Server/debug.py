
##
import hashlib
import os

BufferSize = 1024

File_path = "data/media/"
Log_path = "data/logs/"
File_name = 'f.mp4'



with open(File_path + File_name, 'rb') as file:
    while True:
        l = file.read(BufferSize)
        while l:
            print("Server Says: Sent file chunk {} to  client {}".format(l, idThread))

            l = file.read(BufferSize)
        if not l:
            file.close()
            break