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


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('192.168.0.2', 55554))
    # network = ipaddress.ip_network("172.18.136.0/23")
    network = ipaddress.ip_network("192.168.0.0/24")
    message = add_rand_id(sign(add_timestamp(b"Hello")))
    for i in list(network)[1:-1]:
        s.sendto(message, (str(i), 55555))


if __name__ == "__main__":
    main()