import asyncio
from datetime import datetime

import aiofiles


async def stream_chat(host, port):
    reader, writer = await asyncio.open_connection(host, port)

    while True:
        line = await reader.readline()
        if not line:
            print("No line")
            break
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
        line = f"[{timestamp}] {line.decode().rstrip()}\n"
        print(line, end="")
        async with aiofiles.open("chat.txt", mode="a") as log_file:
            await log_file.writelines(line)


def main():
    asyncio.run(stream_chat("minechat.dvmn.org", 5000))


if __name__ == "__main__":
    main()
