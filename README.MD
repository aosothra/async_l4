# async_l4 - Minechat client scripts

This repository contains client scripts to read from and write to minechat.dvmn.org. 

## Installation and Environment setup

You must have Python3 installed on your system.

You may use `pip` (or `pip3` to avoid conflict with Python2) to install dependencies.

```sh
pip install -r requirements.txt
```

It is strongly advised to use [virtualenv/venv](https://docs.python.org/3/library/venv.html) for project isolation.

## Setup and usage for `chat_reader.py`
`chat_reader.py` outputs chat messages to terminal window and saves them in specified log file. You can use it right out of the box, by running it in python:

```sh
python3 chat_reader.py
```

By that point you should see messages streaming in your terminal window. You may also locate saved chat log `chat.history`, which by default is located in the root directory of your repository. 

Certain customization is supported. Following parameters can be specified as CLI arguments, or defined in `.reader.env` file (you may need to create one).

| Command Line Argument | `.reader.env` key | Default value | Description |
| - | - | - | - |
|  `-H`, `--host` | `HOST` | `minechat.dvmn.org` | Remote host address to connect to |
|  `-P`, `--port` | `PORT` | `5000` | Remote host port to connect to |
|  `-l`, `--log` | `LOG_FILE` | `./chat.history` | Path to chat log to append to |

## Setup and usage for `chat_writer.py`
`chat_writer.py` allows user to send messages to chat, by authenticating them under provided username. It uses `users.json` file to store information with user credentials. If provided username is not present in the file, new user will be registered.

`chat_writer.py` does not require initial setup, and can be used out of the box in the following manner:

```sh
python3 chat_writer.py -u "YourUsername" -m "Hello chat!"
```

Certain customization is supported. Following parameters can be specified as CLI arguments, or defined in `.writer.env` file (you may need to create one).

| Command Line Argument | `.writer.env` key | Default value | Description |
| - | - | - | - |
|  `-H`, `--host` | `HOST` | `minechat.dvmn.org` | Remote host address to connect to |
|  `-P`, `--port` | `PORT` | `5050` | Remote host port to connect to |
|  `-f`, `--users-fullpath` | `USERS_FILE` | `./user.json` | Register file containing users credentials |

## Project goals

This project was created for educational purposes as part of [dvmn.org](https://dvmn.org/) Backend Developer course.