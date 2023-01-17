#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import logging
import signal
import sys
from json import load, dump
from logging.handlers import RotatingFileHandler
from os import popen, system, environ
from os.path import exists
from time import time
from typing import Optional

# noinspection PyPackageRequirements
from Crypto.Hash import SHA256
# noinspection PyPackageRequirements
from Crypto.PublicKey import RSA
# noinspection PyPackageRequirements
from Crypto.Signature import pss

from scripts.exec import commands

if "DEBUG" not in environ.keys():
    key_path = "/etc/schoolDaemon/public.pem"
    config_path = "/etc/schoolDaemon/config.json"
    log_path = "/var/log/schoolDaemon.log"
else:
    key_path = "../public.pem"
    config_path = "../config.json"
    log_path = "../schoolDaemon.log"

rfh = RotatingFileHandler(log_path, maxBytes=1024 * 1024 * 10, backupCount=5)
rfh.setLevel(logging.DEBUG)

sh = logging.StreamHandler()
sh.setLevel(logging.ERROR)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(funcName)s(%(lineno)d) - %(levelname)s - %(message)s",
    handlers=[rfh, sh]
)

logger = logging.getLogger("main")
loop = asyncio.new_event_loop()

with open(key_path, "r") as f:
    key = RSA.import_key(f.read())
    verifier = pss.new(key)

if not exists(config_path):
    with open(config_path, "w") as f:
        dump({"wallpaper": "", "wallpaper_enabled": False}, f)

with open(config_path, "r") as f:
    config = load(f)


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception


# noinspection PyShadowingNames
def exec_script(data: bytes, machine_host: str) -> Optional[bytes]:
    host = data[:16].rstrip(b"q")
    command = data[16:19]
    other_data = data[19:].decode("utf-8")
    
    logger.debug(f"Command: {command} for {host} with data {other_data}")
    
    if host.decode() not in machine_host:
        logger.info(f"Received command for {host}, but this is {machine_host}, ignoring")
        return
    
    if command == b"wae":
        if not config.get("wallpaper", "") and not exists(other_data):
            return
        if exists(other_data):
            config["wallpaper"] = other_data
        config["wallpaper_enabled"] = True
        with open(config_path, "w") as f:
            dump(config, f)
        if "wallpaper" in tasks.keys():
            tasks["wallpaper"].cancel()
            from wallpaper_helper import main as wallpaper_helper
            tasks["wallpaper"] = loop.create_task(handle_cancelled_tasks(wallpaper_helper, config))
        else:
            from wallpaper_helper import main as wallpaper_helper
            tasks["wallpaper"] = loop.create_task(handle_cancelled_tasks(wallpaper_helper, config))
        return b"OK"
    elif command == b"wad":
        config["wallpaper_enabled"] = False
        with open(config_path, "w") as f:
            dump(config, f)
        if "wallpaper" in tasks.keys():
            tasks["wallpaper"].cancel()
            del tasks["wallpaper"]
        return b"OK"
    
    if command not in commands.keys():
        logger.warning(f"Unknown command {command}, ignoring")
        return
    
    shell_command = commands[command]
    logger.debug(f"Executing shell command {shell_command}")
    
    if shell_command.endswith(" "):
        shell_command += other_data
    system(shell_command)
    return b"ok"


class UDPServer(asyncio.DatagramProtocol):
    def __init__(self):
        self.transport = None
        self.machine_host = popen("hostname").read()
        self.last_id = None
    
    def __call__(self, *args, **kwargs):
        return self
    
    def connection_made(self, transport: asyncio.DatagramTransport):
        self.transport = transport
    
    def datagram_received(self, data: bytes, addr: tuple):
        logger.info(f"Received data from {addr}")
        try:
            rand_id = data[:16]
            if self.last_id == rand_id:
                logger.info("Duplicate message, ignoring")
                return
            self.last_id = rand_id
            data = data[16:]
        
            if len(data) <= 128:
                logger.warning("Received data is too short")
                return
        
            calculated_hash = SHA256.new(data[128:])
            try:
                verifier.verify(calculated_hash, data[:128])
            except (ValueError, TypeError):
                logger.warning("Received data is not signed correctly")
                return
        
            data = data[128:]
        
            if time() - int.from_bytes(data[:5], "big") > 5:
                logger.warning("Received data is too old")
                return
        
            data = data[5:]
        
            logger.debug("Executing command")
            result = exec_script(data, self.machine_host)
            if result:
                logger.debug(f"Result: {result}")
                # self.transport.sendto(result, addr)
        except Exception:
            logger.exception("Error while handling data")


tasks = dict()
running = True


def terminate(_: int, __):
    global running
    running = False
    for task in tasks.values():
        task.cancel()
    loop.stop()
    logger.info("SchoolDaemon stopped")


async def handle_cancelled_tasks(coro, *args, **kwargs):
    try:
        await coro(*args, **kwargs)
    except asyncio.CancelledError:
        pass


async def main():
    global tasks, running
    
    _ = await loop.create_datagram_endpoint(
        UDPServer(),
        local_addr=("0.0.0.0", 55555)
    )
    
    if config.get("wallpaper_enabled", False) and "DEBUG" not in environ.keys():
        from wallpaper_helper import main as wallpaper_helper
        tasks["wallpaper"] = loop.create_task(handle_cancelled_tasks(wallpaper_helper, config))


if __name__ == "__main__":
    try:
        signal.signal(signal.SIGTERM, terminate)
    except AttributeError:
        pass
    
    try:
        signal.signal(signal.SIGINT, terminate)
    except AttributeError:
        pass
    
    try:
        signal.signal(signal.SIGQUIT, terminate)
    except AttributeError:
        pass
    
    try:
        signal.signal(signal.SIGHUP, terminate)
    except AttributeError:
        pass

    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(main())
        loop.run_forever()
    except RuntimeError:
        pass
    
    loop.close()
