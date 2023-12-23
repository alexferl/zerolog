import builtins
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, List

import zerolog
from zerolog import constants
from .encoder_json import enc
from .event import Event
from .level import Level

if TYPE_CHECKING:
    from .logger import Logger

# needed because some Context methods name conflict with types
_str = str
_int = int
_float = float
_bool = bool


class TimestampHook:
    def run(self, e: Event, lvl: Level, msg: str):
        e.timestamp()


th = TimestampHook()


@dataclass
class CallerHook:
    caller_skip_frame_count: int = constants.MIN_INT32

    def run(self, e: Event, lvl: Level, msg: str):
        match self.caller_skip_frame_count:
            case constants.MIN_INT32:
                # Extra frames to skip (added by hook infra).
                e.caller(zerolog.CallerSkipFrameCount + 3)
            case _:
                # Extra frames to skip (added by hook infra).
                e.caller(ch.caller_skip_frame_count + 3)


def new_caller_hook(skip_frame_count: int) -> CallerHook:
    return CallerHook(skip_frame_count)


# use_global_skip_frame_count acts as a flag to inform CallerHook.Run
# to use the global CallerSkipFrameCount.
use_global_skip_frame_count = constants.MIN_INT32

# ch is the default caller hook using the global CallerSkipFrameCount.
ch = CallerHook(use_global_skip_frame_count)


# Context configures a new sub-logger with contextual fields.
@dataclass
class Context:
    _l: "Logger"

    # logger returns the logger with the context previously set.
    def logger(self) -> "Logger":
        return self._l

    # exc adds the field "exception" with serialized e to the logger context.
    def exc(self, e: Exception) -> "Context":
        m = zerolog.ExceptionMarshalFunc(e)
        match type(m):
            case builtins.str:
                return self.str(zerolog.ExceptionFieldName, m)
            case Exception():
                return self.str(zerolog.ExceptionFieldName, m)
            case _:
                return self.any(zerolog.ExceptionFieldName, m)

    # any adds the field key with val marshaled using reflection.
    def any(self, key: _str, val: Any) -> "Context":
        self._l._context = enc.append_any(enc.append_key(self._l._context, key), val)
        return self

    # bool adds the field key with val as a bool to the logger context.
    def bool(self, key: _str, val: _bool) -> "Context":
        self._l._context = enc.append_bool(enc.append_key(self._l._context, key), val)
        return self

    # bools adds the field key with vals as a List[bool] to the logger context.
    def bools(self, key: _str, vals: List[_bool]) -> "Context":
        self._l._context = enc.append_bools(enc.append_key(self._l._context, key), vals)
        return self

    # float adds the field key with val as a float to the logger context.
    def float(self, key: _str, val: _float) -> "Context":
        self._l._context = enc.append_float(enc.append_key(self._l._context, key), val)
        return self

    # floats adds the field key with vals as a List[float] to the logger context.
    def floats(self, key: _str, vals: List[_float]) -> "Context":
        self._l._context = enc.append_floats(
            enc.append_key(self._l._context, key), vals
        )
        return self

    # int adds the field key with val as an int to the logger context.
    def int(self, key: _str, val: _int) -> "Context":
        self._l._context = enc.append_int(enc.append_key(self._l._context, key), val)
        return self

    # ints adds the field key with vals as a List[int] to the logger context.
    def ints(self, key: _str, vals: List[_int]) -> "Context":
        self._l._context = enc.append_ints(enc.append_key(self._l._context, key), vals)
        return self

    # str adds the field key with val as a string to the logger context.
    def str(self, key: _str, val: _str) -> "Context":
        self._l._context = enc.append_string(enc.append_key(self._l._context, key), val)
        return self

    # strs adds the field key with vals as a List[str] to the logger context.
    def strs(self, key: _str, vals: List[_str]) -> "Context":
        self._l._context = enc.append_strings(
            enc.append_key(self._l._context, key), vals
        )
        return self

    # timestamp adds the current local time to the logger context with the "time" key,
    # formatted using zerolog.TimeFieldFormat.
    # To customize the key name, change zerolog.TimestampFieldName.
    # To customize the time format, change zerolog.TimeFieldFormat.
    #
    # NOTE: It won't dedupe the "time" key if the *Context has one already.
    def timestamp(self) -> "Context":
        self._l = self._l.hook(th)
        return self

    # caller adds the file:line of the caller with the zerolog.CallerFieldName key.
    def caller(self) -> "Context":
        self._l = self._l.hook(ch)
        return self

    # caller_with_skip_frame_count adds the file:line of the caller with the zerolog.CallerFieldName key.
    # The specified skip_frame_count will override the global CallerSkipFrameCount for this context's respective logger.
    # If set to -1 the global CallerSkipFrameCount will be used.
    def caller_with_skip_frame_count(self, skip_frame_count: _int) -> "Context":
        self._l = self._l.hook(new_caller_hook(skip_frame_count))
        return self

    # stack enables stack trace printing for the exception passed to exc().
    def stack(self) -> "Context":
        self._l._stack = True
        return self
