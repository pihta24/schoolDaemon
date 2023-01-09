#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 55555))
    while True:
        data, addr = s.recvfrom(1024)
        s.sendto(data, addr)


if __name__ == "__main__":
    main()