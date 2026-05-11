import random
import socket
import time


def tcp_check(host: str, port: int, timeout: float = 2.0) -> tuple[bool, float]:
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, round((time.perf_counter() - start) * 1000, 2)
    except OSError:
        return False, 0.0


def mtproto_handshake_probe(host: str, port: int, timeout: float = 3.0) -> bool:
    payload = bytes(random.getrandbits(8) for _ in range(64))
    try:
        with socket.create_connection((host, port), timeout=timeout) as conn:
            conn.settimeout(timeout)
            conn.sendall(payload)
            try:
                conn.recv(1)
            except socket.timeout:
                return True
            return True
    except OSError:
        return False
