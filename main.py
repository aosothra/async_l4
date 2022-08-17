import asyncio
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

import aiofiles


async def stream_chat(host, port, log_fullpath):
    reader, writer = await asyncio.open_connection(host, port)

    while True:
        line = await reader.readline()
        if not line:
            print("No line")
            break
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        line = f"[{timestamp}] {line.decode().rstrip()}\n"
        print(line, end="")
        async with aiofiles.open(log_fullpath, mode="a+") as log_file:
            await log_file.writelines(line)


def main():
    parser = ArgumentParser()
    parser.add_argument("-H", "--host", type=str, required=True, help="Remote host address to connect to")
    parser.add_argument("-P", "--port", type=int, required=True, help="Remote port to connect to")
    parser.add_argument("-l", "--log", type=str, default="chat.history", help="Path to chat log to append to")
    args = parser.parse_args()
    log_fullpath = Path(args.log)
    log_fullpath.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(stream_chat(args.host, args.port, log_fullpath))


if __name__ == "__main__":
    main()
