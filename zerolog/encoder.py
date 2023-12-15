from abc import abstractmethod
from datetime import datetime
from typing import Any, List, Protocol


class Encoder(Protocol):
    @abstractmethod
    def append_any(self, dst: bytes, val: Any) -> bytes:
        pass

    @abstractmethod
    def append_begin_marker(self, dst: bytes) -> bytes:
        pass

    @abstractmethod
    def append_bool(self, dst: bytes, val: bool) -> bytes:
        pass

    @abstractmethod
    def append_bools(self, dst: bytes, val: List[bool]) -> bytes:
        pass

    @abstractmethod
    def append_end_marker(self, dst: bytes) -> bytes:
        pass

    @abstractmethod
    def append_float(self, dst: bytes, val: float) -> bytes:
        pass

    @abstractmethod
    def append_floats(self, dst: bytes, val: List[float]) -> bytes:
        pass

    @abstractmethod
    def append_int(self, dst: bytes, val: int) -> bytes:
        pass

    @abstractmethod
    def append_ints(self, dst: bytes, val: List[int]) -> bytes:
        pass

    @abstractmethod
    def append_key(self, dst: bytes, key: str) -> bytes:
        pass

    @abstractmethod
    def append_line_break(self, dst: bytes) -> bytes:
        pass

    @abstractmethod
    def append_object_data(self, dst: bytes, o: bytes) -> bytes:
        pass

    @abstractmethod
    def append_string(self, dst: bytes, s: str) -> bytes:
        pass

    @abstractmethod
    def append_strings(self, dst: bytes, s: List[str]) -> bytes:
        pass

    @abstractmethod
    def append_time(self, dst: bytes, t: datetime, fmt: str) -> bytes:
        pass
