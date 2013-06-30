import socket
import time
import struct
UDP_IP= "<broadcast>"
UDP_PORT=1985


while True:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))

        data, addr = sock.recvfrom(100)
        print("Message: {}".format(struct.unpack('!Qi',data)))
    except Exception as e:
        print(e)
    time.sleep(1)
    print('.')
