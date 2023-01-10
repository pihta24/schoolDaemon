#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
# noinspection PyPackageRequirements
from Crypto.PublicKey import RSA
# noinspection PyPackageRequirements
from Crypto.Hash import SHA256
# noinspection PyPackageRequirements
from Crypto.Signature import pss
from os import popen, system
from time import time
from scripts.exec import commands


# key_path = "/etc/schoolDaemon/public.pem"
key_path = "../public.pem"


with open(key_path, "r") as f:
    key = RSA.import_key(f.read())
    verifier = pss.new(key)


def check_hostname(host: str) -> bool:
    machine_host = popen("hostname").read()
    return host in machine_host


def exec_script(data: bytes) -> bytes | None:
    host = data[:16].rstrip(b"q")
    command = data[16:19]
    other_data = data[19:]

    if not check_hostname(host.decode()):
        return

    system(commands[command])
    return b"ok"


def main():
    last_id = None
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 55555))
    while True:
        data, addr = s.recvfrom(1024)
        print(data)
        
        rand_id = data[:16]
        if last_id == rand_id:
            continue
        last_id = rand_id
        data = data[16:]
        
        if len(data) <= 128:
            continue
            
        calculated_hash = SHA256.new(data[128:])
        try:
            verifier.verify(calculated_hash, data[:128])
        except (ValueError, TypeError):
            continue
        
        data = data[128:]
        
        if time() - int.from_bytes(data[:5], "big") > 5:
            continue
        
        data = data[5:]
        
        result = exec_script(data)
        if result:
            s.sendto(result, addr)


if __name__ == "__main__":
    main()
