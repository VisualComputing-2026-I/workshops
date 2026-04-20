import asyncio
import json
import random
import signal
from datetime import datetime

import websockets

HOST = "localhost"
PORT = 8765

COLORS = [
    "#ff4d4f",
    "#73d13d",
    "#40a9ff",
    "#ffd666",
    "#9254de",
]


async def stream_data(websocket):
    while True:
        payload = {
            "x": round(random.uniform(-3.5, 3.5), 3),
            "y": round(random.uniform(0.5, 3.0), 3),
            "z": round(random.uniform(-3.5, 3.5), 3),
            "color": random.choice(COLORS),
            "pulse": round(random.uniform(0.7, 1.6), 3),
            "timestamp": datetime.now().isoformat(timespec="milliseconds"),
        }
        print(f"Sending payload: {payload}")
        await websocket.send(json.dumps(payload))
        await asyncio.sleep(0.5)


async def handler(websocket):
    print("Client connected")
    try:
        await stream_data(websocket)
    except websockets.ConnectionClosed:
        print("Client disconnected")


async def main():
    stop = asyncio.Future()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set_result, None)

    async with websockets.serve(handler, HOST, PORT):
        print(f"WebSocket server running on ws://{HOST}:{PORT}")
        await stop


if __name__ == "__main__":
    asyncio.run(main())
