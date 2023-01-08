import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', 768))


def main():
    while True:
        data, addr = s.recvfrom(1024)
        s.sendto(data, addr)
