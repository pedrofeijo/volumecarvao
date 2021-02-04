#!/bin/python3.8
import struct
import numpy
import socket
import sys

def __load(positions):
    numPoints = int(positions.size /3)
    msg = struct.pack('b',1) + struct.pack('i',numPoints) + positions.tobytes()
    # send message to viewer
    __send(msg)
#    print(msg)

def __send(msg):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', _portNumber))
    totalSent = 0
    while totalSent < len(msg):
        sent = s.send(msg)
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalSent = totalSent + sent
    s.close()

args = [[0,0,0],[2,2,2],[1,1,1]]
positions = numpy.asarray(args, dtype=numpy.float32).reshape(-1,3)
print(positions)
if len(sys.argv) == 2:
    _portNumber = int(sys.argv[1])
else:
    print("./teste.py <port number>")
__load(positions)


