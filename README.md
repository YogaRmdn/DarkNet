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

You will be prompted for the server IP and port. Defaults:
- **Host:** `103.253.244.85`
- **Port:** `55555`

You can also pass them as arguments:

```bash
python darknet.py --host <server_ip> --port <port>
```

## Commands

| Command | Description |
|---------|-------------|
| `/help` | Show help |
| `/users` | Show online users |
| `/msg <user>` | Send a private message |
| `/join <room>` | Join a chat room |
| `/leave` | Leave current room |
| `/rooms` | List chat rooms |
| `/nick <name>` | Change username |
| `/create <room>` | Create a new room |
| `/clear` | Clear screen |
| `/exit` | Disconnect and exit |

## Logging

Chat logs are stored in the `logs/` directory with daily rotation.
