import asyncio
import logging
from os import system
from os.path import getmtime
from json import load

logger = logging.getLogger("wallpaper-helper")

with open("/etc/schoolDaemon/config.json", "r") as f:
    config = load(f)


async def main():
    modified = None
    while True:
        if getmtime("/home/student/.config/plasma-org.kde.plasma.desktop-appletsrc") != modified:
            modified = getmtime("/home/student/.config/plasma-org.kde.plasma.desktop-appletsrc")
            with open("/home/student/.config/plasma-org.kde.plasma.desktop-appletsrc", "r") as f:
                data = f.read()
                if config["wallpaper"] not in data:
                    logger.info("Wallpaper not set, setting it")
                    system(
                        f"su - student -c \"DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u student)/bus bash /opt/schoolDaemon/ksetwallpaper.sh {config['wallpaper']}\"")
        await asyncio.sleep(60)


if __name__ == '__main__':
    asyncio.set_event_loop(asyncio.new_event_loop())
    asyncio.run(main())
