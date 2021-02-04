#!/bin/python3.8
import struct
import numpy
import socket

def __load(positions):
    numPoints = int(positions.size /3)
    msg = struct.pack('b',1) + struct.pack('i',numPoints) + positions.tobytes()
    __send(msg)

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
_portNumber = 35637
positions = numpy.asarray([[0,0,0],[2,2,2],[1,1,1]],dtype=numpy.float32)
__load(positions)


