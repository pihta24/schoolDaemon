import io
import logging
from base64 import b64encode

import socketio
from PIL import Image
from mss import mss
from requests import get
from asyncio.queues import Queue

logger = logging.getLogger("screen-streamer")
stream_on = True


async def asyncio_task(host: str, port: int, machine_host: str, queue: Queue):
    global stream_on
    stream_on = True
    logger.info("Starting screen streamer asyncio task")
    get(f"http://{host}:{port}/api/socket").close()
    sio = socketio.AsyncClient()
    await sio.connect(f"http://{host}:{port}/", wait_timeout=60)
    await sio.emit("setType", "daemon")

    @sio.on("stream_off")
    async def stream_off(data):
        global stream_on
        if machine_host.rstrip("\n").rstrip().endswith(data):
            stream_on = False
            await sio.disconnect()

    with mss(display=":0") as stc:
        last_image = None
        while sio.connected and stream_on:
            try:
                img = stc.grab(stc.monitors[1])
                image = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
                image = image.resize((int(image.width / 3), int(image.height / 3)), Image.ANTIALIAS)
                img_b = io.BytesIO()
                image.save(img_b, format="JPEG", quality=85, optimize=True)
                img = "data:image/jpeg;base64," + b64encode(img_b.getvalue()).decode('utf-8')
                if img != last_image or not queue.empty():
                    if not queue.empty():
                        queue.get_nowait()
                    await sio.emit("image", {"image": img, "hostname": machine_host})
                    last_image = img
                await sio.sleep(1 / 5)
            except ConnectionResetError:
                logger.info("Connection reset by peer")
                break
            except Exception:
                logger.exception("Error while streaming screen")
                break
        await sio.disconnect()
    logger.info("Stopping screen streamer")