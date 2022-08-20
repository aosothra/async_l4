import asyncio
from datetime import datetime
from pathlib import Path

import aiofiles
import configargparse
from dotenv import load_dotenv


async def read_chat_stream(host, port, log_fullpath):
    reader, writer = await asyncio.open_connection(host, port)

    try:
        while True:
            line = await reader.readline()
            timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            line = f"[{timestamp}] {line.decode().rstrip()}\n"
            print(line, end="")
            async with aiofiles.open(log_fullpath, mode="a+") as log_file:
                await log_file.writelines(line)
    finally:
        writer.close()
        await writer.wait_closed()


def main():
    load_dotenv(".reader.env")
    parser = configargparse.ArgParser()
    parser.add("-H", "--host", type=str, default="minechat.dvmn.org", help="Remote host address to connect to", env_var="HOST")
    parser.add("-P", "--port", type=int, default="5000", help="Remote port to connect to", env_var="PORT")
    parser.add("-l", "--log", type=str, default="chat.history", help="Path to chat log to append to", env_var="HISTORY_FILE")
    args = parser.parse_args()
    log_fullpath = Path(args.log)
    log_fullpath.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(read_chat_stream(args.host, args.port, log_fullpath))


if __name__ == "__main__":
    main()
