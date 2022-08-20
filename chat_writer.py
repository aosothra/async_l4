import asyncio
import json
import logging
import uuid
from pathlib import Path

import aiofiles
import configargparse
from dotenv import load_dotenv

logger = logging.getLogger(__file__)


async def send_message(writer, message):
    writer.write(message.encode())
    await writer.drain()


async def register(reader, writer, username):
    signin_message = (await reader.readline()).decode().strip()
    logger.debug(f"Message: {signin_message}")
    skip_auth_reply = "\n"
    await send_message(writer, skip_auth_reply)
    logger.debug(f"Reply: {skip_auth_reply.strip()}")

    request_username_message = (await reader.readline()).decode().strip()
    logger.debug(f"Message: {request_username_message}")
    username_reply = f"{username}\n"
    await send_message(writer, username_reply)
    logger.debug(f"Reply: {username_reply.strip()}")

    signup_result = json.loads((await reader.readline()).decode())

    logger.debug(f"Message: {signup_result}")
    logger.debug(f"Registered as {signup_result['nickname']}.")

    return signup_result['account_hash']


async def authorize(reader, writer, user_hash):
    signin_message = (await reader.readline()).decode().strip()
    logger.debug(f"Message: {signin_message}")
    user_hash_reply = f"{user_hash}\n"
    await send_message(writer, user_hash_reply)
    logger.debug(f"Reply: {user_hash_reply.strip()}")

    auth_result = json.loads((await reader.readline()).decode())
    logger.debug(f"Message: {auth_result}")
    if auth_result is None:
        raise ValueError("User hash is invalid, check credentials or try to register first")
    else:
        logger.debug(f"Logged in as {auth_result['nickname']}")


async def broadcast_to_chat(host, port, users_fullpath, username, message):
    reader, writer = await asyncio.open_connection(host, port)

    users = dict()
    user_hash = None

    if Path(users_fullpath).exists():
        async with aiofiles.open(users_fullpath, "rb") as users_file:
            try:
                users = json.loads(await users_file.read())
                user_hash = users.get(username, None)
            except json.JSONDecodeError:
                logger.warning("User register is empty.")
    
    try:
        if not user_hash:
            user_hash = await register(reader, writer, username)
            users[username] = user_hash
            async with aiofiles.open(users_fullpath, "wb") as users_file:
                await users_file.write(json.dumps(users).encode())
        else:
            await authorize(reader, writer, user_hash)

        await send_message(writer, f"{message}\n\n")
        logger.debug(f"Broadcast: {message}")
    finally:
        writer.close()
        await writer.wait_closed()


def main():
    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__file__)
    logger.setLevel(logging.DEBUG)

    load_dotenv(".writer.env")
    parser = configargparse.ArgParser()
    parser.add("-H", "--host", type=str, default="minechat.dvmn.org", help="Remote host address to connect to", env_var="HOST")
    parser.add("-P", "--port", type=int, default="5050", help="Remote port to connect to", env_var="PORT")
    parser.add("-f", "--users-fullpath", type=str, default="users.json", help="Full path to JSON file with users", env_var="USERS_FILE")
    parser.add("-u", "--user", type=str, required=True, help="Username to acquire user credentials")
    parser.add("-m", "--message", type=str, required=True, help="Message to broadcast")
    args = parser.parse_args()
    
    users_fullpath = Path(args.users_fullpath)
    users_fullpath.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(broadcast_to_chat(args.host, args.port, users_fullpath, args.user, args.message))


if __name__ == "__main__":
    main()