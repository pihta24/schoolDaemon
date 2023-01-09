import socket
import ipaddress


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 55554))
    network = ipaddress.ip_network("172.18.136.0/23")
    for i in list(network)[1:-1]:
        s.sendto(b"Hello", (str(i), 55555))


if __name__ == "__main__":
    main()