import asyncio
import json
import logging
import uuid
from argparse import ArgumentParser
from pathlib import Path

import aiofiles


logger = logging.getLogger(__file__)


async def register(reader, writer, username):
    signin_message = (await reader.readline()).decode().strip()
    logger.debug(f"Message: {signin_message}")
    skip_auth_reply = "\n"
    writer.write(skip_auth_reply.encode())
    await writer.drain()
    logger.debug(f"Reply: {skip_auth_reply.strip()}")

    request_username_message = (await reader.readline()).decode().strip()
    logger.debug(f"Message: {request_username_message}")
    username_reply = f"{username}\n"
    writer.write(username_reply.encode())
    await writer.drain()
    logger.debug(f"Reply: {username_reply.strip()}")

    signup_result = json.loads((await reader.readline()).decode())

    logger.debug(f"Message: {signup_result}")
    logger.debug(f"Registered as {signup_result['nickname']}.")

    return signup_result['account_hash']


async def authorize(reader, writer, user_hash):
    signin_message = (await reader.readline()).decode().strip()
    logger.debug(f"Message: {signin_message}")
    user_hash_reply = f"{user_hash}\n"
    writer.write(user_hash_reply.encode())
    await writer.drain()
    logger.debug(f"Reply: {user_hash_reply.strip()}")

    auth_result = json.loads((await reader.readline()).decode())
    logger.debug(f"Message: {auth_result}")
    if auth_result is None:
        raise ValueError("User hash is invalid, check credentials or try to register first")
    else:
        logger.debug(f"Logged in as {auth_result['nickname']}")


async def send_message(host, port, username, message):
    reader, writer = await asyncio.open_connection(host, port)

    users = dict()
    user_hash = None

    if Path("users.json").exists():
        async with aiofiles.open("users.json", "rb") as users_file:
            try:
                users = json.loads(await users_file.read())
                user_hash = users.get(username, None)
            except json.JSONDecodeError:
                logger.warning("User register is empty.")
    
    try:
        if user_hash is None:
            user_hash = await register(reader, writer, username)
            users[username] = user_hash
            async with aiofiles.open("users.json", "wb") as users_file:
                await users_file.write(json.dumps(users).encode())
        else:
            await authorize(reader, writer, user_hash)

        writer.write(f"{message}\n\n".encode())
        await writer.drain()
        logger.debug(f"Broadcast: {message}")
    finally:
        writer.close()
        await writer.wait_closed()

def main():
    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__file__)
    logger.setLevel(logging.DEBUG)

    parser = ArgumentParser()
    parser.add_argument("-H", "--host", type=str, required=True, help="Remote host address to connect to")
    parser.add_argument("-P", "--port", type=int, required=True, help="Remote port to connect to")
    parser.add_argument("-u", "--user", type=str, required=True, help="Username to acquire user credentials")
    parser.add_argument("-m", "--message", type=str, required=True, help="Message to broadcast")
    args = parser.parse_args()
    
    asyncio.run(send_message(args.host, args.port, args.user, args.message))


if __name__ == "__main__":
    main()