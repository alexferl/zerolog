import sys
from dataclasses import dataclass, field
from datetime import datetime
from inspect import getframeinfo, stack
from typing import Any, Callable, IO, List

import zerolog
from .encoder_json import enc
from .hook import Hook
from .level import Level

# needed because some Event methods name conflict with types
_str = str
_int = int
_float = float
_bool = bool


# Event represents a log event. It is instanced by one of the level method of
# Logger and finalized by the msg or send method.
@dataclass(slots=True)
class Event:
    _buf: bytes = b""
    _w: IO | None = None
    _level: Level = Level.TraceLevel
    _done: Callable[[str], None] | None = None
    _stack: bool = False  # enable error stack trace
    _ch: List[Hook] = field(default_factory=lambda: [])  # hooks from context
    _skip_frames: int = (
        0  # The number of additional frames to skip when printing the caller.
    )

    # enabled return false if the Event is going to be filtered out by
    # log level or sampling.
    def enabled(self) -> bool:
        return self._level != Level.Disabled

    # discard disables the event so msg() won't print it.
    def discard(self):
        self._level = Level.Disabled
        return

    # msg sends the Event with msg added as the message field if not empty.
    #
    # NOTICE: once this method is called, the Event should be disposed.
    # Calling msg twice can have unexpected result.
    def msg(self, msg: str):
        self._msg(msg)

    # send is equivalent to calling msg("").
    #
    # NOTICE: once this method is called, the Event should be disposed.
    def send(self):
        self._msg("")

    def _msg(self, msg: _str):
        try:
            for hook in self._ch:
                hook.run(self, self._level, msg)
            if msg != "":
                self._buf = enc.append_string(
                    enc.append_key(self._buf, zerolog.MessageFieldName), msg
                )
            try:
                self._write()
            except Exception as e:
                if zerolog.ExceptionHandler is not None:
                    zerolog.ExceptionHandler(e)
                else:
                    print(f"zerolog: could not write event: {e}", file=sys.stderr)
        finally:
            if self._done is not None:
                self._done(msg)

    def _write(self):
        if self._level != Level.Disabled:
            self._buf = enc.append_end_marker(self._buf)
            self._buf = enc.append_line_break(self._buf)
            if self._w is not None:
                self._w.write(self._buf)
                if hasattr(self._w, "seek"):
                    self._w.seek(0)

    # func allows an anonymous function to run only if the event is enabled.
    def func(self, f: Callable[["Event"], None]) -> "Event":
        if self.enabled():
            f(self)
        return self

    # bool adds the field key with i as a bool to the Event context.
    def bool(self, key: _str, i: _bool) -> "Event":
        self._buf = enc.append_bool(enc.append_key(self._buf, key), i)
        return self

    # bools adds the field key with i as a List[bool] to the Event context.
    def bools(self, key: _str, i: List[_bool]) -> "Event":
        self._buf = enc.append_bools(enc.append_key(self._buf, key), i)
        return self

    # float adds the field key with i as a float to the Event context.
    def float(self, key: _str, i: _float) -> "Event":
        self._buf = enc.append_float(enc.append_key(self._buf, key), i)
        return self

    # floats adds the field key with i as a List[float] to the Event context.
    def floats(self, key: _str, i: List[_float]) -> "Event":
        self._buf = enc.append_floats(enc.append_key(self._buf, key), i)
        return self

    # int adds the field key with i as a int to the Event context.
    def int(self, key: _str, i: _int) -> "Event":
        self._buf = enc.append_int(enc.append_key(self._buf, key), i)
        return self

    # ints adds the field key with i as a List[int] to the Event context.
    def ints(self, key: _str, i: List[_int]) -> "Event":
        self._buf = enc.append_ints(enc.append_key(self._buf, key), i)
        return self

    # string adds the field key with val as a string to the Event context.
    def str(self, key: str, val: str) -> "Event":
        self._buf = enc.append_string(enc.append_key(self._buf, key), val)
        return self

    # strs adds the field key with vals as a List[str] to the Event context.
    def strs(self, key: _str, vals: List[_str]) -> "Event":
        self._buf = enc.append_strings(enc.append_key(self._buf, key), vals)
        return self

    # any adds the field key with val marshaled using reflection.
    def any(self, key: _str, val: Any) -> "Event":
        self._buf = enc.append_any(enc.append_key(self._buf, key), val)
        return self

    # exc adds the field "exception" with serialized e to the Event context.
    #
    # To customize the key name, change zerolog.ExceptionFieldName.
    #
    # If stack() has been called before and zerolog.ExceptionStackMarshaler is defined,
    # the e is passed to ExceptionStackMarshaler and the result is appended to the
    # zerolog.ExceptionStackFieldName.
    def exc(self, e: Exception) -> "Event":
        if self._stack and zerolog.ExceptionStackMarshaler is not None:
            m = zerolog.ExceptionStackMarshaler(e)
            match type(m):
                case None:
                    pass
                case str():
                    self.str(zerolog.ExceptionStackFieldName, m)
                case _:
                    if issubclass(m.__class__, Exception):
                        return self.str(zerolog.ExceptionFieldName, str(m))
                    self.any(zerolog.ExceptionStackFieldName, m)

        m = zerolog.ExceptionMarshalFunc(e)
        match type(m):
            case None:
                return self
            case str():
                return self.str(zerolog.ExceptionFieldName, m)
            case _:
                if issubclass(m.__class__, Exception):
                    return self.str(zerolog.ExceptionFieldName, str(m))
                return self.any(zerolog.ExceptionFieldName, m)

    # stack enables stack trace printing for the error passed to exc().
    #
    # ExceptionStackMarshaler must be set for this method to do something.
    def stack(self) -> "Event":
        self._stack = True
        return self

    # timestamp adds the current local time as UNIX timestamp to the Event context with the "time" key.
    # To customize the key name, change zerolog.TimestampFieldName.
    #
    # NOTE: It won't dedupe the "time" key if the Event (or Context) has one
    # already.
    def timestamp(self) -> "Event":
        self._buf = enc.append_time(
            enc.append_key(self._buf, zerolog.TimestampFieldName),
            zerolog.TimestampFunc(),
            zerolog.TimeFieldFormat,
        )
        return self

    # time adds the field key with t formatted as string using zerolog.TimeFieldFormat.
    def time(self, key: _str, t: datetime) -> "Event":
        self._buf = enc.append_time(
            enc.append_key(self._buf, key), t, zerolog.TimeFieldFormat
        )
        return self

    # caller_skip_frame instructs any future caller calls to skip the specified number of frames.
    # This includes those added via hooks from the context.
    def caller_skip_frame(self, skip: _int) -> "Event":
        self._skip_frames += skip
        return self

    # Caller adds the file:line of the caller with the zerolog.CallerFieldName key.
    # The argument skip is the number of stack frames to ascend
    # skip If not passed, use the global variable CallerSkipFrameCount
    def caller(self, *skip: _int) -> "Event":
        sk = zerolog.CallerSkipFrameCount
        if len(skip) > 0:
            sk = skip[0] + zerolog.CallerSkipFrameCount
        return self._caller(sk)

    def _caller(self, skip: _int) -> "Event":
        try:
            tb = getframeinfo(stack()[skip][0])
        except Exception as e:
            print(f"zerolog: could not get traceback: {e}", file=sys.stderr)
            return self
        self._buf = enc.append_string(
            enc.append_key(self._buf, zerolog.CallerFieldName),
            zerolog.CallerMarshalFunc(tb),
        )
        return self


def _new_event(w: IO | None, lvl: Level) -> Event:
    e = Event()
    e._ch = []
    e._buf = enc.append_begin_marker(e._buf)
    e._w = w
    e._level = lvl
    e._stack = False
    e._skip_frames = 0
    return e
