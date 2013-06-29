import socket
import time
UDP_IP= "192.168.1.107"
UDP_PORT=5637


while True:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))
    
        data, addr = sock.recvfrom(1)
        print("Message: {}".format(data))
    except Exception:
        pass
    time.sleep(1)
    print('.')
