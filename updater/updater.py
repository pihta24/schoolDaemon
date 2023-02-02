#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from os import system, popen
from os.path import exists
from aiorun import run


async def main():
    while True:
        await asyncio.sleep(200)
        if exists("/root/schoolDaemon"):
            if "Your branch is up to date with 'origin/master'." not in popen(
                    "cd /root/schoolDaemon && git remote update && git status -uno").read():
                system("cd /root/schoolDaemon && git pull && python3 setup.py 3")
        else:
            system("cd /root && git clone https://github.com/pihta24/schoolDaemon.git")
            system("cd /root/schoolDaemon && python3 setup.py 3")
        await asyncio.sleep(3400)

if __name__ == "__main__":
    run(main(), stop_on_unhandled_errors=True)
