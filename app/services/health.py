import random
import socket
import time
from typing import Tuple


def tcp_check(host: str, port: int, timeout: float = 2.0) -> Tuple[bool, float]:
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            rtt = (time.perf_counter() - start) * 1000
            return True, round(rtt, 2)
    except OSError:
        return False, 0.0


def mtproto_handshake_probe(host: str, port: int, timeout: float = 3.0) -> bool:
    # Lightweight synthetic MTProto probe: send 64-byte random init payload
    # and require connection not to be instantly reset.
    payload = bytes(random.getrandbits(8) for _ in range(64))
    try:
        with socket.create_connection((host, port), timeout=timeout) as conn:
            conn.settimeout(timeout)
            conn.sendall(payload)
            try:
                _ = conn.recv(1)
            except socket.timeout:
                return True
            return True
    except OSError:
        return False
