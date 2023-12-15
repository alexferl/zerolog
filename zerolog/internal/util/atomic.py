import threading


class Int:
    def __init__(self, init: int = 0):
        self._value = init
        self._lock = threading.Lock()

    def store(self, num: int) -> int:
        with self._lock:
            self._value = num
            return self._value

    def load(self) -> int:
        with self._lock:
            return self._value
