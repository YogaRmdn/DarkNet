#!/usr/bin/env python3
"""
ShadowNet Terminal Chat - Standalone Client
Single file, no dependencies except: pip install rich prompt-toolkit
"""
import socket
import json
import sys
import os
import time
import threading
import logging
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.markup import escape
from prompt_toolkit import PromptSession, print_formatted_text, prompt
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter, Completer, Completion
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.styles import Style


VERSION = "1.0"
UPDATE_URL = "https://raw.githubusercontent.com/YogaRmdn/DarkNet/main/darknet.py"
DEFAULT_HOST = ""
DEFAULT_PORT = 55555

USER_COLORS = [
    "bright_green", "bright_cyan", "bright_yellow", "green", "cyan", "yellow",
    "bright_magenta", "bright_red",
]


# ==================== LOGGER ====================

class ChatLogger:
    def __init__(self, name="shadownet"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.handlers:
            os.makedirs("logs", exist_ok=True)
            fh = logging.FileHandler(f"logs/client_{datetime.now().strftime('%Y%m%d')}.log", encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
            self.logger.addHandler(fh)

    def info(self, msg): self.logger.info(msg)
    def debug(self, msg): self.logger.debug(msg)
    def error(self, msg): self.logger.error(msg)


# ==================== UI ====================

def pt(text):
    return print_formatted_text(HTML(text))

class ChatUI:
    def __init__(self):
        self.console = Console()
        self.current_room = "general"
        self.username = ""
        self.online_users = []

    BANNER = """
██████╗  █████╗ ██████╗ ██╗  ██╗███╗   ██╗███████╗████████╗
██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝████╗  ██║██╔════╝╚══██╔══╝
██║  ██║███████║██████╔╝█████╔╝ ██╔██╗ ██║█████╗     ██║
██║  ██║██╔══██║██╔══██╗██╔═██╗ ██║╚██╗██║██╔══╝     ██║
██████╔╝██║  ██║██║  ██║██║  ██╗██║ ╚████║███████╗   ██║
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝
"""

    def banner(self):
        from rich.text import Text
        t = Text(self.BANNER, style="bold bright_green")
        t.append("\n ┌──", style="bright_green")
        t.append(" DARKNET v" + VERSION, style="bright_yellow")
        t.append(" :: ", style="bright_green")
        t.append("internet on the internet", style="bright_cyan")
        t.append("\n ├─", style="bright_green")
        t.append(" https://github.com/YogaRmdn", style="bright_cyan")
        t.append("\n └──", style="bright_green")
        t.append(" Developed by Bangyog", style="bright_yellow")
        t.append("\n", style="bright_green")
        self.console.print(t)

    def out(self, text):
        pt(text)

    def system(self, msg, ts=None):
        ts = ts or datetime.now().strftime("%H:%M:%S")
        self.out(f"<dim><style fg='#00aa00'>{ts}</style></dim> <b><style fg='#00ff00'>[>]</style></b> <style fg='#00ff00'>{_e(msg)}</style>")

    def message(self, user, content, ts, room=None, color="bright_green"):
        t = f"<dim><style fg='#00aa00'>{ts}</style></dim>"
        u = f"<b><{color}>{_e(user)}</{color}></b>"
        r = f" <dim><style fg='#00aa00'>({room})</style></dim>" if room and room != self.current_room else ""
        self.out(f"{t}{r} {u}: {_e(content)}")

    def private(self, from_user, content, ts, sent=False):
        t = f"<dim><style fg='#00aa00'>{ts}</style></dim>"
        arrow = "<b><cyan>[-&gt;]</cyan></b>" if sent else "<b><cyan>[&lt;-]</cyan></b>"
        tag = "<b><bright_yellow>PRIVATE</bright_yellow></b>"
        u = f"<b><bright_green>{_e(from_user)}</bright_green></b>"
        self.out(f"{t} {arrow} {tag} {u}: <bright_cyan>{_e(content)}</bright_cyan>")

    def error(self, msg):
        self.out(f"<b><bright_red>[!]</bright_red></b> <bright_red>{_e(msg)}</bright_red>")

    def info(self, msg):
        self.out(f"<b><bright_green>[*]</bright_green></b> <bright_green>{_e(msg)}</bright_green>")

    def users(self, users):
        if not users:
            self.out("<yellow>[!] No users online</yellow>")
        else:
            ul = ", ".join(f"<bright_green>{_e(u)}</bright_green>" for u in users)
            self.out(f"<b><style fg='#00ff00'>ONLINE</style></b> (<bright_green>{len(users)}</bright_green>): {ul}")

    def rooms(self, rooms, current):
        self.out("<b><style fg='#00ff00'>ROOMS:</style></b>")
        for r in rooms:
            s = "<b><bright_green>●</bright_green></b>" if r == current else "<dim><style fg='#005500'>○</style></dim>"
            self.out(f"  {s} <bright_green>#{r}</bright_green>")

    def joined(self, room, members=None):
        self.out(f"<b><bright_green>[+]</bright_green></b> <bright_green>Joined #{_e(room)}</bright_green>")
        if members:
            ml = ", ".join(f"<bright_green>{_e(m)}</bright_green>" for m in members)
            self.out(f"  <dim><style fg='#00aa00'>Members: {ml}</style></dim>")

    def left(self, room):
        self.out(f"<b><bright_yellow>[-]</bright_yellow></b> <bright_yellow>Left #{_e(room)}</bright_yellow>")

    def nick(self, old, new):
        self.out(f"<b><bright_yellow>[*]</bright_yellow></b> <bright_green>{_e(old)}</bright_green> → <b><bright_green>{_e(new)}</bright_green></b>")

    HELP_TEXT = """
[bright_green]┌──────────────────────────────────────────┐[/]
[bright_green]│[/]  [bold bright_yellow]DARKNET — AVAILABLE COMMANDS[/]          [bright_green]│[/]
[bright_green]└──────────────────────────────────────────┘[/]

  [bold bright_green]/help[/]        [bright_white]Show this help[/bright_white]
  [bold bright_green]/users[/]       [bright_white]Show online users[/bright_white]
  [bold bright_green]/msg <user>[/]  [bright_white]Send a private message[/bright_white]
  [bold bright_green]/join <room>[/] [bright_white]Join a chat room[/bright_white]
  [bold bright_green]/rooms[/]       [bright_white]List available rooms[/bright_white]
  [bold bright_green]/create <room>[/] [bright_white]Create a new room[/bright_white]
  [bold bright_green]/nick <name>[/] [bright_white]Change your username[/bright_white]
  [bold bright_green]/clear[/]       [bright_white]Clear the screen[/bright_white]
  [bold bright_green]/update[/]      [bright_white]Auto-update from remote URL[/bright_white]
  [bold bright_green]/exit[/]        [bright_white]Disconnect and exit[/bright_white]

[bright_black]Tip: Just type a message and press Enter to broadcast it.[/]
"""


def _e(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ==================== COMPLETER ====================

class CommandCompleter(Completer):
    def __init__(self):
        self.commands = [
            "/help", "/users", "/msg", "/join", "/rooms",
            "/nick", "/create", "/clear", "/update", "/exit"
        ]

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if not text.startswith("/"):
            return
        for cmd in self.commands:
            if cmd.startswith(text):
                yield Completion(cmd, start_position=-len(text))


# ==================== CLIENT ====================

class ShadowClient:
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.sock = None
        self.username = ""
        self.current_room = "general"
        self.connected = False
        self.online_users = []
        self.ui = ChatUI()
        self.logger = ChatLogger()
        self.auth_event = threading.Event()
        self.auth_error = ""
        self._running = True
        self._user_colors = {}
        self._color_idx = 0

    def send(self, data):
        try:
            self.sock.sendall((json.dumps(data, ensure_ascii=False) + "\n").encode("utf-8"))
            return True
        except OSError:
            self.connected = False
            return False

    def run(self):
        try:
            self.ui.banner()
            self.ui.info(f"Connecting to {self.host}:{self.port}...")

            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10)
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.sock.connect((self.host, self.port))
            self.sock.settimeout(None)
            self.connected = True
            self.ui.info(f"Connected to server at {self.host}:{self.port}")

            recv = threading.Thread(target=self._recv_loop, daemon=True)
            recv.start()

            while self._running:
                username = self.ui.console.input("[#00ff00]└─[/] [#00ff00]Username[/] [#00ff00]:[/] ").strip()
                if not username:
                    continue
                if not username.replace("_", "").isalnum():
                    self.ui.error("Username must be alphanumeric (underscore allowed)")
                    continue
                if len(username) > 20:
                    self.ui.error("Username too long (max 20)")
                    continue

                password = prompt(HTML("<style fg='#00ff00'>└─</style> <style fg='#00ff00'>Password</style> <style fg='#00ff00'>:</style> "), is_password=True).strip()
                if password != "whoami":
                    self.ui.error("Access denied: invalid password")
                    continue

                authenticated = False
                while self._running:
                    self.auth_event.clear()
                    self.auth_error = ""
                    self.send({"type": "auth", "username": username})

                    if not self.auth_event.wait(timeout=15):
                        self.ui.error("Authentication timed out")
                        break

                    if self.auth_error:
                        if "taken" in self.auth_error.lower():
                            time.sleep(0.5)
                            continue
                        self.ui.error(self.auth_error)
                        break

                    authenticated = True
                    self.username = username
                    self.ui.username = username
                    self.ui.info(f"Welcome, {username}! Type /help for commands.")
                    self.ui.console.print("[#005500]═" * 50 + "[/]")
                    self.ui.console.print("[bold #00ff00]  CONNECTION ESTABLISHED  >>  [/][#00aa00]encrypted[/]  [bold #00ff00]>>[/]  [#005500]DARKNET[/]")
                    self.ui.console.print(f"[#005500]═[/]" * 50)
                    break

                if authenticated:
                    break

            self._send_loop()

        except (ConnectionRefusedError, TimeoutError, OSError) as e:
            self.ui.error(f"Cannot connect: {e}")
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

    def _recv_loop(self):
        buf = ""
        while self._running and self.connected:
            try:
                data = self.sock.recv(65536)
                if not data:
                    break
                buf += data.decode("utf-8")
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                        self._dispatch(msg)
                    except json.JSONDecodeError:
                        continue
            except OSError:
                break
        self.connected = False

    def _get_user_color(self, name):
        if name not in self._user_colors:
            self._user_colors[name] = USER_COLORS[self._color_idx % len(USER_COLORS)]
            self._color_idx += 1
        return self._user_colors[name]

    def _dispatch(self, msg):
        t = msg.get("type", "")

        if t == "broadcast":
            color = self._get_user_color(msg["username"])
            self.ui.message(msg["username"], msg["content"], msg.get("timestamp",""), msg.get("room"), color)
        elif t == "system":
            self.ui.system(msg["message"], msg.get("timestamp"))
        elif t == "private":
            self.ui.private(msg["from"], msg["content"], msg.get("timestamp",""), sent=False)
        elif t == "private_sent":
            self.ui.private(msg["to"], msg["content"], msg.get("timestamp",""), sent=True)
        elif t == "error":
            self.ui.error(msg.get("message", "Unknown error"))
        elif t == "user_list":
            old_count = len(self.online_users)
            self.online_users = msg.get("users", [])
            for u in self.online_users:
                self._get_user_color(u)
            new_count = len(self.online_users)
            if new_count != old_count and old_count != 0:
                self.ui.system(f"Online users: {new_count}")
        elif t == "join_ok":
            room = msg.get("room", "")
            self.current_room = room
            self.ui.joined(room, msg.get("members"))
        elif t == "leave_ok":
            room = msg.get("room", "general")
            self.current_room = room
            self.ui.left(room)
        elif t == "nick_ok":
            old, new = msg.get("old_name",""), msg.get("new_name","")
            self.username = new
            self.ui.nick(old, new)
        elif t == "command_result":
            s = msg.get("subtype", "")
            if s == "users":
                self.ui.users(msg.get("users", []))
            elif s == "rooms":
                self.ui.rooms(msg.get("rooms", []), msg.get("current_room", ""))
            else:
                m = msg.get("message", "")
                if m:
                    self.ui.info(m)
        elif t == "auth_ok":
            self.ui.info(msg.get("message", ""))
            self.ui.users(msg.get("online_users", []))
            self.auth_event.set()
        elif t == "auth_error":
            self.auth_error = msg.get("message", "")
            self.auth_event.set()
        elif t == "info":
            self.ui.info(msg.get("message", ""))

    def _self_update(self):
        import urllib.request
        url = os.environ.get("SHADOWNET_UPDATE_URL") or UPDATE_URL
        if not url:
            self.ui.error("UPDATE_URL is not set. Set SHADOWNET_UPDATE_URL env or edit UPDATE_URL in script.")
            return
        self.ui.info("Downloading update...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ShadowNet-Updater/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                new_code = r.read().decode("utf-8")
            script_path = os.path.abspath(__file__)
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(new_code)
            self.ui.info("Update applied! Restarting...")
            time.sleep(1)
            os.execv(sys.executable, [sys.executable, script_path] + sys.argv[1:])
        except Exception as e:
            self.ui.error(f"Update failed: {e}")

    def _send_loop(self):
        style = Style.from_dict({"prompt": "bold #00ff00"})
        session = PromptSession(
            history=InMemoryHistory(),
            auto_suggest=AutoSuggestFromHistory(),
            completer=CommandCompleter(),
            style=style,
        )

        with patch_stdout():
            while self._running and self.connected:
                try:
                    online_count = len(self.online_users)
                    room_label = f"#{self.current_room}"
                    status_style = "bold #00aa00" if online_count > 0 else "dim #005500"
                    status_text = f"[{online_count} online]" if online_count > 0 else "[0 online]"
                    txt = session.prompt([
                        ("bold #00ff00", f"┌─({room_label}) "),
                        (status_style, status_text),
                        ("", "\n"),
                        ("bold #00ff00", "└─❯ "),
                    ]).strip()
                    if not txt:
                        continue

                    if txt == "/exit" or txt == "/quit":
                        break
                    if txt == "/clear":
                        os.system("cls" if os.name == "nt" else "clear")
                        continue
                    if txt == "/help":
                        self.ui.out(self.ui.HELP_TEXT)
                        continue
                    if txt == "/update":
                        self._self_update()
                        continue
                    if txt.startswith("/leave"):
                        self.ui.error("Feature /leave is disabled. This is a permanent group chat.")
                        continue

                    if txt.startswith("/"):
                        self.send({"type": "command", "command": txt.lstrip("/")})
                    else:
                        if len(txt) > 2000:
                            self.ui.error("Message too long (max 2000)")
                        else:
                            self.send({"type": "message", "content": txt})

                except (EOFError, KeyboardInterrupt):
                    break

        self.send({"type": "disconnect"})

    def cleanup(self):
        self._running = False
        self.connected = False
        if self.sock:
            try:
                self.send({"type": "disconnect"})
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try: self.sock.close()
            except OSError: pass
        print("\n└─ Connection closed. Goodbye.")


def main():
    import argparse
    p = argparse.ArgumentParser(description="ShadowNet Terminal Chat Client")
    p.add_argument("--host", default=None, help="Server IP")
    p.add_argument("--port", type=int, default=None, help="Server port")
    args = p.parse_args()

    console = Console()
    host = args.host or os.environ.get("SHADOWNET_HOST")
    if not host:
        host = console.input("[#00ff00]└─[/] [#00ff00]Server IP[/] [#00ff00]:[/] ").strip()
    port = args.port or (lambda x: int(x) if x else DEFAULT_PORT)(
        os.environ.get("SHADOWNET_PORT") or console.input(f"[#00ff00]└─[/] [#00ff00]Port[/] [#00ff00]({DEFAULT_PORT})[/] [#00ff00]:[/] ").strip()
    )

    ShadowClient(host=host, port=port).run()


if __name__ == "__main__":
    main()
