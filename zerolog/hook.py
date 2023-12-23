from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Protocol

from .level import Level

if TYPE_CHECKING:
    from .event import Event


# Hook defines an interface to a log hook.
class Hook(Protocol):
    @abstractmethod
    def run(self, e: "Event", level: Level, msg: str):
        pass


# HookFunc is an adaptor to allow the use of an ordinary function
# as a Hook.
class HookFunc:
    def __init__(self, func: Callable[["Event", Level, str], None]):
        self.func = func

    def run(self, e: "Event", level: Level, message: str) -> None:
        self.func(e, level, message)


# LevelHook applies a different hook for each level.
@dataclass
class LevelHook:
    no_level_hook: Hook | None = None
    trace_hook: Hook | None = None
    debug_hook: Hook | None = None
    info_hook: Hook | None = None
    warn_hook: Hook | None = None
    error_hook: Hook | None = None
    fatal_hook: Hook | None = None

    def run(self, e: "Event", lvl: Level, msg: str):
        match lvl:
            case Level.TraceLevel:
                if self.trace_hook is not None:
                    self.trace_hook.run(e, lvl, msg)
            case Level.DebugLevel:
                if self.debug_hook is not None:
                    self.debug_hook.run(e, lvl, msg)
            case Level.InfoLevel:
                if self.info_hook is not None:
                    self.info_hook.run(e, lvl, msg)
            case Level.WarnLevel:
                if self.warn_hook is not None:
                    self.warn_hook.run(e, lvl, msg)
            case Level.ErrorLevel:
                if self.error_hook is not None:
                    self.error_hook.run(e, lvl, msg)
            case Level.FatalLevel:
                if self.fatal_hook is not None:
                    self.fatal_hook.run(e, lvl, msg)
            case Level.NoLevel:
                if self.no_level_hook is not None:
                    self.no_level_hook.run(e, lvl, msg)


# new_level_hook returns a new LevelHook.
def new_level_hook() -> LevelHook:
    return LevelHook()
