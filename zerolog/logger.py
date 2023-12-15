from dataclasses import dataclass, field
from typing import Any, Callable, IO, List

import zerolog
from .context import Context
from .encoder_json import enc
from .event import Event, _new_event
from .hook import Hook
from .level import Level
from .sampler import Sampler


# A Logger represents an active logging object that generates lines
# of JSON output to an IO. Each logging operation makes a single
# call to the IO's write method. There is no guarantee on access
# serialization to the IO. If your IO is not thread safe,
# you may consider a sync wrapper.
@dataclass
class Logger:
    _w: IO | None
    _level: Level = Level.DebugLevel
    _sampler: Sampler | None = None
    _context: bytes = b""
    _hooks: List[Hook] = field(default_factory=lambda: [])
    _stack: bool = False

    def output(self, w: IO) -> "Logger":
        l: Logger = new(w)
        l._level = self._level
        l._sampler = self._sampler
        l._stack = self._stack
        if len(self._hooks) > 0:
            l._hooks = self._hooks
        if self._context is not None:
            l._context = self._context
        return l

    # level creates a child logger with the minimum accepted level set to level.
    def level(self, lvl: Level) -> "Logger":
        self._level = lvl
        return self

    # get_level returns the current Level.
    def get_level(self) -> Level:
        return self._level

    # Sample returns a logger with the s sampler.
    def sample(self, s: Sampler) -> "Logger":
        self._sampler = s
        return self

    # ctx creates a child logger with the field added to its context.
    def ctx(self) -> Context:
        context = self._context
        logger = new(self._w)
        if len(context) > 0:
            logger._context += context
        else:
            # This is needed for append_key to not check len of input
            # thus making it inlinable
            logger._context = enc.append_begin_marker(self._context)

        return Context(logger)

    def hook(self, h: Hook) -> "Logger":
        self._hooks.append(h)
        return self

    # trace starts a new message with trace level.
    #
    # You must call msg on the returned event in order to send the event.
    def trace(self) -> Event | None:
        return self.new_event(Level.TraceLevel, None)

    # debug starts a new message with debug level.
    #
    # You must call msg on the returned event in order to send the event.
    def debug(self) -> Event | None:
        return self.new_event(Level.DebugLevel, None)

    # info starts a new message with info level.
    #
    # You must call msg on the returned event in order to send the event.
    def info(self) -> Event | None:
        return self.new_event(Level.InfoLevel, None)

    # warn starts a new message with warn level.
    #
    # You must call msg on the returned event in order to send the event.
    def warn(self) -> Event | None:
        return self.new_event(Level.WarnLevel, None)

    # error starts a new message with error level.
    #
    # You must call msg on the returned event in order to send the event.
    def error(self) -> Event | None:
        return self.new_event(Level.ErrorLevel, None)

    # fatal starts a new message with fatal level.
    #
    # You must call msg on the returned event in order to send the event.
    def fatal(self) -> Event | None:
        return self.new_event(Level.FatalLevel, lambda msg: exit(1))

    # exception starts a new message with error level.
    #
    # You must call msg on the returned event in order to send the event.
    def exc(self, e: Exception) -> Event | None:
        err = self.error()
        if err is not None:
            return err.exc(e)
        return None

    # with_level starts a new message with lvl. Unlike the fatal
    # method, with_level does not terminate the program.
    #
    # You must call msg on the returned event in order to send the event.
    def with_level(self, lvl: Level) -> Event | None:
        match lvl:
            case Level.TraceLevel:
                return self.trace()
            case Level.DebugLevel:
                return self.debug()
            case Level.InfoLevel:
                return self.info()
            case Level.WarnLevel:
                return self.warn()
            case lvl.ErrorLevel:
                return self.error()
            case lvl.FatalLevel:
                return self.new_event(Level.FatalLevel, None)
            case lvl.NoLevel:
                return self.log()
            case lvl.Disabled:
                return
            case _:
                return self.new_event(lvl, None)

    # log starts a new message with no level. Setting GlobalLevel to Disabled
    # will still disable events produced by this method.
    #
    # You must call msg on the returned event in order to send the event.
    def log(self) -> Event | None:
        return self.new_event(Level.NoLevel, None)

    # print sends a log event using debug level and no extra field.
    def print(self, *args: Any):
        e = self.debug()
        if e and e.enabled():
            e.msg("".join((str(x) for x in args)))

    def new_event(self, lvl: Level, done: Callable[[str], None] | None) -> Event | None:
        enabled = self._should(lvl)
        if not enabled:
            if done is not None:
                done("")
            return None
        e: Event = _new_event(self._w, lvl)
        e._done = done
        e._ch = self._hooks
        if lvl != Level.NoLevel and zerolog.LevelFieldName != "":
            e.str(zerolog.LevelFieldName, lvl.string())
        if len(self._context) > 1:
            e._buf = enc.append_object_data(e._buf, self._context)
        return e

    def _should(self, lvl: Level) -> bool:
        if self._w is None:
            return False
        if lvl < self._level or lvl < zerolog.global_level():
            return False
        if self._sampler is not None and zerolog.sampling_disabled is False:
            return self._sampler.sample(lvl)
        return True


def new(w: IO | None) -> Logger:
    return Logger(w)


def nop() -> Logger:
    return new(None).level(Level.Disabled)
