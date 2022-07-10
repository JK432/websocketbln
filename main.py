import asyncio
import logging
import websockets
from websockets import WebSocketServerProtocol
from websockets import WebSocketClientProtocol

logging.basicConfig(level=logging.INFO)


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol) -> None:
        self.clients.add(ws)
        logging.info(f"{ws.remote_adress} connects")

    async def unregister(self, ws: WebSocketServerProtocol) -> None:
        self.clients.remove(ws)
        logging.info(f"{ws.remote_adress} disconnets")

    async def send_to_clients(self, message: str) -> None:
        if self.clients:
            await  asyncio.wait([client.send(message) for client in self.clients])

    async def distribute(self, ws: WebSocketServerProtocol) -> None:
        async  for message in ws:
            await self.send_to_clients(message)

    async def wc_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distribute(ws)
        finally:
            await  self.unregister(ws)


async def produce(message: str, host: str, port: int) -> None:
    async with websockets.connect(f"ws://{host}:{port}") as ws:
        await ws.send(message)
        await ws.recv()


async def cosumer_handler(websocket: WebSocketClientProtocol) -> None:
    async for message in websocket:
        log_message(message)


async def consume(hostname: str, port: int) -> None:
    websocket_resource_url = f"ws://{hostname}:{port}"
    async with websockets.connect(websocket_resource_url ) as websocket:
        await cosumer_handler(websocket)


def log_message(message: str) -> None:
    logging.info(f"Message:{message}")


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    server = Server()

    start_server = websockets.serve(server.wc_handler, 'localhost', 4000)
    loop.run_until_complete(start_server)
    loop.run_forever()