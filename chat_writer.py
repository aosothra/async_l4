import asyncio
import json
import uuid
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

import aiofiles


async def register(host, port, username):
    reader, writer = await asyncio.open_connection(host, port)

    print(await reader.readline())
    writer.write("\n".encode())
    await writer.drain()
    print(await reader.readline())
    writer.write(f"{username}\n".encode())
    await writer.drain()
    print(await reader.readline())
    writer.close()
    await writer.wait_closed()


async def authorize(host, port, user_uuid):
    reader, writer = await asyncio.open_connection(host, port)
    print(await reader.readline())
    writer.write(f"{user_uuid}\n".encode())
    await writer.drain()
    auth_result = json.loads((await reader.readline()).decode())
    writer.close()
    await writer.wait_closed()
    if auth_result is None:
        print("User UUID is invalid, check credentials or try to register first")
    else:
        print(f"Logged in as {auth_result['nickname']}")



def main():
    parser = ArgumentParser()
    parser.add_argument("-H", "--host", type=str, required=True, help="Remote host address to connect to")
    parser.add_argument("-P", "--port", type=int, required=True, help="Remote port to connect to")
    parser.add_argument("-u", "--user", type=str, required=True, help="UUID for login, or username for registration")
    args = parser.parse_args()
    try:
        user_uuid = uuid.UUID(args.user)
    except ValueError:
        username = args.user
    
    print(user_uuid)
    if user_uuid is not None:
        asyncio.run(authorize(args.host, args.port, user_uuid))
    else:
        asyncio.run(register(args.host, args.port, username))


if __name__ == "__main__":
    main()