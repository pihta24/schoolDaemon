import asyncio
from queue import Empty
from mss.linux import MSS
from mss import mss as sct
import logging
from mss.tools import to_png


logger = logging.getLogger("screen-streamer")


async def asyncio_task(host: str, port: int):
    logger.info("Starting screen streamer asyncio task")
    reader, writer = await asyncio.open_connection(host, port)
    logger.info("Connected to server")
    logger.info("Starting screen streamer")
    # with MSS(":0") as mss:
    with sct() as mss:
        while True:
            try:
                img = mss.grab(mss.monitors[1])
                img = to_png(img.rgb, img.size)
                writer.write(img + b"EOFEOFEOF")
                await writer.drain()
                await asyncio.sleep(1 / 10)
            except ConnectionResetError:
                logger.info("Connection reset by peer")
                break
            except Exception:
                logger.exception("Error while streaming screen")
                writer.close()
                raise
    logger.info("Stopping screen streamer")
