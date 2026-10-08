import asyncio

async def handle_client(reader, writer):
    try:
        while True:
            data = await reader.read(100)
            if not data:
                break
            message = data.decode()
            addr = writer.get_extra_info('peername')
            print(f"Received {message!r} from {addr!r}")
            writer.write(data)
            await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()

async def client():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    try:
        message = 'Hello, world'
        print(f'Send: {message!r}')
        writer.write(message.encode())
        await writer.drain()
        
        data = await reader.read(100)
        print(f'Received: {data.decode()!r}')

        for i in range(3):
            data = await reader.read(100)
            print(f'Received: {data.decode()!r}')
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())