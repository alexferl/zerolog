import threading


class Int:
    def __init__(self, init: int = 0):
        self._value = init
        self._lock = threading.Lock()

    def add(self, delta: int) -> int:
        with self._lock:
            self._value += delta
            return self._value

    def compare_and_swap(self, old: int, new: int) -> bool:
        with self._lock:
            if self._value != old:
                return False
            self._value = new
            return True

    def load(self) -> int:
        with self._lock:
            return self._value

    def store(self, val: int) -> int:
        with self._lock:
            self._value = val
            return self._value

    def swap(self, new: int) -> int:
        with self._lock:
            val = self._value
            self._value = new
            return val
