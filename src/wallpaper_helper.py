import asyncio
import logging
from os import system
from os.path import getmtime, exists
from shutil import copy2

logger = logging.getLogger("wallpaper-helper")


async def main(config):
    modified = None
    logger.info("Starting wallpaper daemon")
    while True:
        if getmtime("/home/student/.config/plasma-org.kde.plasma.desktop-appletsrc") != modified:
            modified = getmtime("/home/student/.config/plasma-org.kde.plasma.desktop-appletsrc")
            if "wallpaper" not in config.keys():
                continue
            if not config["wallpaper_enabled"]:
                continue
            if not exists(config["wallpaper"]):
                continue
            with open("/home/student/.config/plasma-org.kde.plasma.desktop-appletsrc", "r") as f:
                data = f.read()
                logger.info("Wallpaper not set, setting it")
                copy2("/opt/schoolDaemon/ksetwallpaper.sh", "/home/student/.schd/ksetwallpaper.sh")
                system("chmod ugo+rx /home/student/.schd/ksetwallpaper.sh")
                system(
                    f"su - student -c \"DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u student)/bus bash /home/student/.schd/ksetwallpaper.sh {config['wallpaper']}\"")
                system("rm /home/student/.schd/ksetwallpaper.sh")
                modified = getmtime("/home/student/.config/plasma-org.kde.plasma.desktop-appletsrc")
        await asyncio.sleep(60)
