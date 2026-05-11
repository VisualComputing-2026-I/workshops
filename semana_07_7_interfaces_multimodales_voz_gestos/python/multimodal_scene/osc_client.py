from __future__ import annotations

from pythonosc.udp_client import SimpleUDPClient


class OscStateClient:
    def __init__(self, enabled: bool, host: str, port: int) -> None:
        self._enabled = enabled
        self._client = SimpleUDPClient(host, port) if enabled else None

    def send(self, address: str, value) -> None:
        if not self._enabled or self._client is None:
            return
        self._client.send_message(address, value)
