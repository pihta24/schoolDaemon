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
                await asyncio.sleep(60)
                continue
            if not config["wallpaper_enabled"]:
                await asyncio.sleep(60)
                continue
            if not exists(config["wallpaper"]):
                await asyncio.sleep(60)
                continue
            logger.info("Wallpaper not set, setting it")
            if not exists("/home/student/.schd"):
                system("mkdir -p /home/student/.schd")
                system("chown student:student /home/student/.schd")
                system("chmod 766 /home/student/.schd")
            copy2("/opt/schoolDaemon/ksetwallpaper.sh", "/home/student/.schd/ksetwallpaper.sh")
            system("chmod ugo+rx /home/student/.schd/ksetwallpaper.sh")
            system(
                f"su - student -c \"DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u student)/bus bash /home/student/.schd/ksetwallpaper.sh {config['wallpaper']}\"")
            system("rm /home/student/.schd/ksetwallpaper.sh")
            modified = getmtime("/home/student/.config/plasma-org.kde.plasma.desktop-appletsrc")
        await asyncio.sleep(60)
