#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from shutil import copytree, copy2
from os import system, popen
from sys import argv
from os.path import exists


def install():
    system("apt-get install xinput")
    system("python3 -m ensurepip")
    system("python3 -m pip install pycryptodome")
    copytree("./src", "/opt/schoolDaemon")
    system("chown -R root:root /opt/schoolDaemon")
    system("chmod -R 770 /opt/schoolDaemon")
    system("mkdir /etc/schoolDaemon")
    copy2("./public.pem", "/etc/schoolDaemon/public.pem")
    system("chmod -R 770 /etc/schoolDaemon")
    copy2("./schoolDaemon.service", "/etc/systemd/system")
    system("chown root:root /etc/systemd/system/schoolDaemon.service")
    system("chmod 644 /etc/systemd/system/schoolDaemon.service")
    system("systemctl daemon-reload")
    system("systemctl enable schoolDaemon.service")
    system("systemctl start schoolDaemon.service")


def uninstall():
    system("systemctl stop schoolDaemon.service")
    system("systemctl disable schoolDaemon.service")
    system("rm -rf /opt/schoolDaemon")
    system("rm /etc/systemd/system/schoolDaemon.service")
    system("systemctl daemon-reload")
    system("rm -rf /etc/schoolDaemon")


def update():
    system("systemctl stop schoolDaemon.service")
    system("rm -rf /opt/schoolDaemon")
    copytree("./src", "/opt/schoolDaemon")
    system("chown -R root:root /opt/schoolDaemon")
    system("chmod -R 770 /opt/schoolDaemon")
    system("systemctl start schoolDaemon.service")


def auto_update():
    if exists("/root/schoolDaemon"):
        if "Your branch is up to date with 'origin/master'." not in popen(
                "cd /root/schoolDaemon && git remote update && git status -uno").read():
            system("cd /root/schoolDaemon && git pull && python3 setup.py 3")
    else:
        system("cd /root && git clone https://github.com/pihta24/schoolDaemon.git")
        system("cd /root/schoolDaemon && python3 setup.py 3")


def main():
    if len(argv) >= 2:
        if argv[1] == "1":
            install()
        if argv[1] == "2":
            uninstall()
        if argv[1] == "3":
            update()
        if argv[1] == "4":
            auto_update()
        return
    print("Welcome to the schoolDaemon installer!")
    print("Please choose what you want to do:")
    print("1. Install")
    print("2. Uninstall")
    print("3. Update")
    print("4. Exit")
    while choice := input("Your choice: "):
        if choice == "4":
            break
        if choice == "1":
            install()
            break
        elif choice == "2":
            uninstall()
            break
        elif choice == "3":
            update()
            break
        else:
            print("Invalid choice!")
            print("Please choose what you want to do:")
            print("1. Install")
            print("2. Uninstall")
            print("3. Update")
            print("4. Exit")


if __name__ == "__main__":
    main()
