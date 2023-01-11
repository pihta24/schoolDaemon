#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import ipaddress
# noinspection PyPackageRequirements
from Crypto.PublicKey import RSA
# noinspection PyPackageRequirements
from Crypto.Hash import SHA256
# noinspection PyPackageRequirements
from Crypto.Signature import pss
from secrets import token_bytes
from time import time


# key_path = "/etc/schoolDaemon/private.pem"
key_path = "./private.pem"


with open(key_path, "r") as f:
    key = RSA.import_key(f.read())
    signer = pss.new(key)


def sign(msg: bytes) -> bytes:
    h = SHA256.new(msg)
    signature = signer.sign(h)
    return signature + msg


def add_rand_id(msg: bytes) -> bytes:
    return token_bytes(16) + msg


def add_timestamp(msg: bytes) -> bytes:
    return int(time()).to_bytes(5, "big") + msg


def add_hostname(msg: bytes, host: str) -> bytes:
    host_bytes = host.encode()
    return host_bytes + b"q" * (16 - len(host_bytes)) + msg


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 55554))
    network = ipaddress.ip_network("172.18.136.0/23")
    # network = ipaddress.ip_network("192.168.0.0/24")
    
    network = list(network)[1:-1]
    
    print("""Commands:
    ffx(url) - Firefox (requires url without spaces)
    blc - Block
    ubl - Unblock
    ntf(msg) - Notify (requires msg without spaces)
    pau - Policy Auth
    pno - Policy No
    shd - Shutdown
    rbt - Reboot
    los - Logout Student
    pip - Pip Install
    est - Enable System Settings
    dst - Disable System Settings
    """)
    
    while command := input("Command: "):
        for host in network:
            msg = add_rand_id(sign(add_timestamp(add_hostname(command.encode(), "alpha-310"))))
            s.sendto(msg, (str(host), 55555))
    # message = add_rand_id(sign(add_timestamp(add_hostname(b"001", "alpha-310"))))
    # for i in network:
    #     s.sendto(message, (str(i), 55555))
    # data, addr = s.recvfrom(1024)
    # print(data)


if __name__ == "__main__":
    main()
