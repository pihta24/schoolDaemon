#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import logging
import sys
from logging.handlers import RotatingFileHandler
from os import popen, system
from time import time
from typing import Optional

# noinspection PyPackageRequirements
from Crypto.Hash import SHA256
# noinspection PyPackageRequirements
from Crypto.PublicKey import RSA
# noinspection PyPackageRequirements
from Crypto.Signature import pss

from scripts.exec import commands

key_path = "/etc/schoolDaemon/public.pem"
# key_path = "../public.pem"

with open(key_path, "r") as f:
    key = RSA.import_key(f.read())
    verifier = pss.new(key)

rfh = RotatingFileHandler("./schoolDaemon.log", maxBytes=1024 * 1024 * 10, backupCount=5)
rfh.setLevel(logging.DEBUG)

sh = logging.StreamHandler()
sh.setLevel(logging.ERROR)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(funcName)s(%(lineno)d) - %(levelname)s - %(message)s",
    handlers=[rfh, sh]
)

logger = logging.getLogger("main")


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception


def exec_script(data: bytes, machine_host: str) -> Optional[bytes]:
    host = data[:16].rstrip(b"q")
    command = data[16:19]
    other_data = data[19:]
    
    logger.debug(f"Command: {command} for {host} with data {other_data}")
    
    if host.decode() not in machine_host:
        logger.info(f"Received command for {host}, but this is {machine_host}, ignoring")
        return
    
    if command not in commands.keys():
        logger.warning(f"Unknown command {command}, ignoring")
        return
    
    shell_command = commands[command]
    logger.debug(f"Executing shell command {shell_command}")
    
    if shell_command.endswith(" "):
        shell_command += other_data.decode()
    system(shell_command)
    return b"ok"


def main():
    logger.info("Starting schoolDaemon")
    machine_host = popen("hostname").read()
    last_id = None
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    logger.debug("Binding to port 55555")
    s.bind(('', 55555))
    
    logger.debug("Starting main loop")
    while True:
        data, addr = s.recvfrom(1024)
        
        logger.info(f"Received data from {addr}")
        
        rand_id = data[:16]
        if last_id == rand_id:
            logger.info("Duplicate message, ignoring")
            continue
        last_id = rand_id
        data = data[16:]
        
        if len(data) <= 128:
            logger.warning("Received data is too short")
            continue
        
        calculated_hash = SHA256.new(data[128:])
        try:
            verifier.verify(calculated_hash, data[:128])
        except (ValueError, TypeError):
            logger.warning("Received data is not signed correctly")
            continue
        
        data = data[128:]
        
        if time() - int.from_bytes(data[:5], "big") > 5:
            logger.warning("Received data is too old")
            continue
        
        data = data[5:]
        
        logger.debug("Executing command")
        result = exec_script(data, machine_host)
        if result:
            logger.debug(f"Result: {result}")
            s.sendto(result, addr)


if __name__ == "__main__":
    main()
