import socket
from dataclasses import dataclass

PACKET_SIZE = 4


@dataclass(frozen=True)
class ButtonPress:
    address: int
    command: int


class RemoteListener:
    """Receives IR button presses the ESP32 forwards as 'K' <address:u16 LE> <command:u8>."""

    def __init__(self, sock: socket.socket):
        self.sock = sock

    @classmethod
    def bind(cls, port: int) -> "RemoteListener | None":
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.bind(("0.0.0.0", port))
        except OSError:
            sock.close()
            return None
        sock.setblocking(False)
        return cls(sock)

    def poll(self) -> ButtonPress | None:
        try:
            data = self.sock.recv(64)
        except BlockingIOError:
            return None
        if len(data) != PACKET_SIZE or data[:1] != b"K":
            return None
        return ButtonPress(address=int.from_bytes(data[1:3], "little"), command=data[3])
