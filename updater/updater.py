#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from os import system, popen
from os.path import exists

if exists("/root/schoolDaemon"):
    if "Your branch is up to date with 'origin/master'." not in popen(
            "cd /root/schoolDaemon && git remote update && git status -uno").read():
        system("cd /root/schoolDaemon && git pull && python3 setup.py 4")
else:
    system("cd /root && git clone https://github.com/pihta24/schoolDaemon.git")
    system("cd /root/schoolDaemon && python3 setup.py 4")
