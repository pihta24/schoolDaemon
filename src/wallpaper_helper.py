import asyncio
import logging
from os import system
from os.path import getmtime

logger = logging.getLogger("wallpaper-helper")


async def main(config):
    modified = None
    while True:
        if getmtime("/home/student/.config/plasma-org.kde.plasma.desktop-appletsrc") != modified:
            modified = getmtime("/home/student/.config/plasma-org.kde.plasma.desktop-appletsrc")
            if "wallpaper" not in config.keys():
                continue
            with open("/home/student/.config/plasma-org.kde.plasma.desktop-appletsrc", "r") as f:
                data = f.read()
                if config["wallpaper"] not in data:
                    logger.info("Wallpaper not set, setting it")
                    system(
                        f"su - student -c \"DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u student)/bus bash /opt/schoolDaemon/ksetwallpaper.sh {config['wallpaper']}\"")
        await asyncio.sleep(60)
