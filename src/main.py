#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import logging
import socket
import sys
from asyncio.queues import Queue
from json import load, dump
from logging.handlers import RotatingFileHandler
from os import popen, system, environ
from os.path import exists
from time import time
from typing import Optional
from requests import post

from aiorun import run

# noinspection PyPackageRequirements
from Crypto.Hash import SHA256
# noinspection PyPackageRequirements
from Crypto.PublicKey import RSA
# noinspection PyPackageRequirements
from Crypto.Signature import PKCS1_PSS as pss

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
rand_id = None
last_stream = None
streamer_queue = Queue()


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
    global last_stream
    host = data[:20].rstrip(b"q").decode()
    command = data[20:23]
    other_data = data[23:].decode("utf-8")

    logger.debug(f"Command: {command} for {host} with data {other_data}")

    host_len = len(host.split("-"))

    if host_len == 3:
        machine_host_part = machine_host.rstrip("\n").rstrip()
    elif host_len == 2:
        machine_host_part = "-".join(machine_host.rstrip("\n").rstrip().split("-")[:-1])
    elif host_len == 1:
        machine_host_part = "-".join(machine_host.rstrip("\n").rstrip().split("-")[:-2])
    else:
        logger.warning("Received malformed hostname")
        return

    if not machine_host_part.endswith(host):
        logger.info(f"Received command for {host}, but this is {machine_host}, ignoring")
        return

    if command == b"wae":
        if not config.get("wallpaper", "") and not exists(other_data):
            return b"ERR - File not found"
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
    elif command == b"dwa":
        if len(other_data.split()) != 2:
            return

        remote_path, local_folder = other_data.split()
        remote_zip = remote_path.split("/")[-1]

        system(f"wget {remote_path} && "
               f"unzip {remote_zip} -d {remote_zip.replace('.zip', '')} && "
               f"mkdir /usr/share/wallpapers/{local_folder} && "
               f"cp -r -f {remote_zip.replace('.zip', '')}/. /usr/share/wallpapers/{local_folder} && "
               f"rm -rf {remote_zip.replace('.zip', '')} && "
               f"rm -f {remote_zip}")
        return b"OK"
    elif command == b"son":
        if not other_data:
            return b"ERR - No data"
        if "screen_streamer_task" in tasks.keys():
            if tasks["screen_streamer_task"].done():
                del tasks["screen_streamer_task"]
        if "screen_streamer_task" in tasks.keys() and other_data == last_stream:
            loop.create_task(streamer_queue.put(b"OK"))
            return b"Not needed, already streaming"
        elif "screen_streamer_task" in tasks.keys():
            stop_screen_streamer()
        host, port = other_data.split(":")
        start_screen_streamer(host, int(port), machine_host)
        last_stream = other_data
        return b"OK"
    elif command == b"sof":
        stop_screen_streamer()
        return b"OK"
    elif command == "sip":
        if not other_data:
            return b"ERR - No data"
        address, secret = other_data.split()
        post(f"http://{address}/api/ip", json={
            "hostname": "-".join(machine_host.rstrip("\n").rstrip().split("-")[-3:]),
            "ip": ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1])[0],
            "secret": secret
        }).close()
        return b"OK"

    if command not in commands.keys():
        logger.warning(f"Unknown command {command}, ignoring")
        return

    shell_command = commands[command]
    logger.debug(f"Executing shell command {shell_command}")

    if shell_command.endswith(" "):
        shell_command += '"' + other_data + '"'
    system(shell_command)
    return b"OK"


def start_screen_streamer(host: str, port: int, computer: str):
    from screen_streamer import asyncio_task as screen_streamer_task
    tasks["screen_streamer_task"] = asyncio.create_task(handle_cancelled_tasks(screen_streamer_task, host, port, computer, streamer_queue))


def stop_screen_streamer():
    if "screen_streamer_task" in tasks.keys():
        tasks["screen_streamer_task"].cancel()
        del tasks["screen_streamer_task"]


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
        global rand_id
        logger.info(f"Received data from {addr}")
        # noinspection PyBroadException
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


async def handle_cancelled_tasks(coro, *args, **kwargs):
    try:
        await coro(*args, **kwargs)
    except asyncio.CancelledError:
        pass


async def main():
    global tasks

    _ = await loop.create_datagram_endpoint(
        UDPServer(),
        local_addr=("0.0.0.0", 55555)
    )

    if config.get("wallpaper_enabled", False) and "DEBUG" not in environ.keys():
        from wallpaper_helper import main as wallpaper_helper
        tasks["wallpaper"] = loop.create_task(handle_cancelled_tasks(wallpaper_helper, config))

    if config.get("wol", True) and "DEBUG" not in environ.keys():
        system("apt-get install ethtool -y && ethtool -s enp2s0 wol g")


if __name__ == "__main__":
    run(main(), loop=loop, timeout_task_shutdown=5)
