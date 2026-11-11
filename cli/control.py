import socket

CONTROL_ADDR = ("127.0.0.1", 7778)
REPLY_TIMEOUT = 1.0
MAX_MESSAGE = 1024

Address = tuple[str, int]


class ControlServer:
    """Receives text commands from other local processes, e.g. `reggie.py --off`."""

    def __init__(self, sock: socket.socket):
        self.sock = sock

    @classmethod
    def bind(cls) -> "ControlServer | None":
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.bind(CONTROL_ADDR)
        except OSError:
            sock.close()
            return None
        sock.setblocking(False)
        return cls(sock)

    def poll(self) -> tuple[str, Address] | None:
        try:
            data, sender = self.sock.recvfrom(MAX_MESSAGE)
        except BlockingIOError:
            return None
        return data.decode(errors="ignore").strip(), sender

    def reply(self, sender: Address, message: str) -> None:
        self.sock.sendto(message.encode(), sender)


def send_command(command: str) -> str | None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(REPLY_TIMEOUT)
        sock.sendto(command.encode(), CONTROL_ADDR)
        try:
            return sock.recv(MAX_MESSAGE).decode()
        except (TimeoutError, ConnectionRefusedError):
            return None
