import asyncio
import json
import logging
import uuid
from argparse import ArgumentParser


logging.basicConfig(level=logging.ERROR)


async def register(host, port, username):
    logger = logging.getLogger(__file__)
    reader, writer = await asyncio.open_connection(host, port)

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
    print(f"Registered as {signup_result['nickname']}. Your hash for future login:")
    print(signup_result['account_hash'])

    return writer


async def authorize(host, port, user_uuid):
    logger = logging.getLogger(__file__)
    reader, writer = await asyncio.open_connection(host, port)

    signin_message = (await reader.readline()).decode().strip()
    logger.debug(f"Message: {signin_message}")
    user_hash_reply = f"{user_uuid}\n"
    writer.write(user_hash_reply.encode())
    await writer.drain()
    logger.debug(f"Reply: {user_hash_reply.strip()}")

    auth_result = json.loads((await reader.readline()).decode())
    logger.debug(f"Message: {auth_result}")
    if auth_result is None:
        writer.close()
        await writer.wait_closed()
        raise ValueError("User hash is invalid, check credentials or try to register first")
    else:
        print(f"Logged in as {auth_result['nickname']}")
        return writer



def main():
    logger = logging.getLogger(__file__)
    logger.setLevel(logging.DEBUG)

    parser = ArgumentParser()
    parser.add_argument("-H", "--host", type=str, required=True, help="Remote host address to connect to")
    parser.add_argument("-P", "--port", type=int, required=True, help="Remote port to connect to")
    parser.add_argument("-u", "--user", type=str, required=True, help="Hash for login, or username for registration")
    args = parser.parse_args()

    username = user_uuid = None
    try:
        user_uuid = uuid.UUID(args.user)
    except ValueError:
        username = args.user
    
    if user_uuid is not None:
        asyncio.run(authorize(args.host, args.port, user_uuid))
    else:
        asyncio.run(register(args.host, args.port, username))


if __name__ == "__main__":
    main()