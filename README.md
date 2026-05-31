# ShadowNet Terminal Chat

A secure, fast, and professional terminal-based chat client built with Python.

## Features

- Real-time messaging with multiple users
- Private messaging (`/msg <user>`)
- Chat rooms (`/join`, `/leave`, `/create`, `/rooms`)
- Username management (`/nick`)
- User presence tracking (`/users`)
- Color-coded usernames
- Persistent chat logging
- Rich terminal UI with syntax highlighting

## Requirements

- Python 3.8+
- See `requirements.txt` for Python dependencies

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python darknet.py
```

You will be prompted for the server IP and port. Default port: `55555`.

You can also pass them as arguments or use environment variables:

```bash
python darknet.py --host <server_ip> --port <port>
SHADOWNET_HOST=<ip> SHADOWNET_PORT=<port> python darknet.py
```

## Commands

| Command | Description |
|---------|-------------|
| `/help` | Show help |
| `/users` | Show online users |
| `/msg <user>` | Send a private message |
| `/join <room>` | Join a chat room |
| `/rooms` | List chat rooms |
| `/nick <name>` | Change username |
| `/create <room>` | Create a new room |
| `/clear` | Clear screen |
| `/update` | Auto-update from remote URL |
| `/exit` | Disconnect and exit |

## Auto-Update

Set `UPDATE_URL` in the script or use the `SHADOWNET_UPDATE_URL` environment variable to enable `/update`:

```bash
SHADOWNET_UPDATE_URL="https://raw.githubusercontent.com/username/repo/main/darknet.py" python darknet.py
```

## Logging

Chat logs are stored in the `logs/` directory with daily rotation.

