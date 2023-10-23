import os
import socket
from typing import Any, Dict

from ..config import Config
from .command import Command


class ControlCommand(Command):
    def __init__(self, args: Any, config: Config, env: Dict[str, str]):
        Command.__init__(self, args, config, env)
        self.command = args.command
        self.quiet = args.quiet
        self.conn = None

    def execute(self) -> int:
        # Get control socket path from environment
        control_sock = os.environ.get("ASCIINEMA_CTL")
        if control_sock is None:
            self.print_error("ASCIINEMA_CTL environment variable not set; not running in recording session?")
            return 1
        self.conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self.conn.connect(control_sock)
        except OSError as e:
            self.print_error("Failed to connect to control socket: " + str(e))
            return 1
        retval = self.control()
        self.conn.close()
        return retval

    def control(self) -> int:
        if self.command == "pause":
            self.conn.sendall(b"p")
            result = self.conn.recv(128).decode("utf-8").strip()
            if result == "OK":
                if not self.quiet: self.print("Paused recording")
                return 0
            else:
                self.print_error("Failed to pause recording: " + result)
                return 1
        elif self.command == "resume":
            self.conn.sendall(b"r")
            result = self.conn.recv(128).decode("utf-8").strip()
            if result == "OK":
                if not self.quiet: self.print("Resumed recording")
                return 0
            else:
                self.print_error("Failed to pause recording: " + result)
                return 1
        elif self.command == "mark":
            self.conn.sendall(b"m")
            result = self.conn.recv(128).decode("utf-8").strip()
            if result == "OK":
                if not self.quiet: self.print("Added marker")
                return 0
            else:
                self.print_error("Failed to add marker: " + result)
                return 1
        elif self.command == "status":
            self.conn.sendall(b"s")
            result = self.conn.recv(128).decode("utf-8").strip()
            self.print("Recording status: " + result)
            return 0
        else:
            self.print_error("Unknown command: " + self.command)
            return 1
