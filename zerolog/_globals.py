import json
from datetime import datetime
from functools import partial
from inspect import Traceback
from typing import Any, Dict, Callable

from .constants import TimeFormatRFC3339Ms
from .internal.util.atomic import Int
from .level import Level

# _TimestampFieldName is the field name used for the timestamp field.
_TimestampFieldName = "time"

# _LevelFieldName is the field name used for the level field.
_LevelFieldName = "level"

# _LevelTraceValue is the value used for the trace level field.
_LevelTraceValue = "trace"
# _LevelDebugValue is the value used for the debug level field.
_LevelDebugValue = "debug"
# _LevelInfoValue is the value used for the info level field.
_LevelInfoValue = "info"
# _LevelWarnValue is the value used for the warn level field.
_LevelWarnValue = "warn"
# _LevelErrorValue is the value used for the error level field.
_LevelErrorValue = "error"
# _LevelFatalValue is the value used for the fatal level field.
_LevelFatalValue = "fatal"

# _MessageFieldName is the field name used for the message field.
_MessageFieldName = "message"

# _ExceptionFieldName is the field name used for exception fields.
_ExceptionFieldName = "exception"

# _CallerFieldName is the field name used for caller field.
_CallerFieldName = "caller"

# _CallerSkipFrameCount is the number of stack frames to skip to find the caller.
_CallerSkipFrameCount = 1


def _caller_marshal_func(tb: Traceback) -> str:
    return f"{tb.filename}:{tb.lineno}"


# _CallerMarshalFunc allows customization of global caller marshaling
_CallerMarshalFunc = _caller_marshal_func

# _ExceptionStackFieldName is the field name used for exception stacks.
_ExceptionStackFieldName = "stack"

# _ExceptionStackMarshaler extract the stack from e if any.
_ExceptionStackMarshaler: Callable[[Exception], Any] | None = None


def _exception_marshal_func(e: Exception) -> Any:
    return e


# _ExceptionMarshalFunc allows customization of global exception marshaling
_ExceptionMarshalFunc = _exception_marshal_func

# _AnyMarshalFunc allows customization of any marshaling.
_AnyMarshalFunc = json.dumps

# _TimeFieldFormat defines the time format of the time field type. If set to
# TimeFormatUnix, TimeFormatUnixMs or TimeFormatUnixMicro the time is formatted as a UNIX
# timestamp as integer. If set to TimeFormatRFC3339, TimeFormatRFC3339Ms or
# TimeFormatRFC3339Micro the time is formatted as a RFC3339 date string.
_TimeFieldFormat = TimeFormatRFC3339Ms

# _TimestampFunc defines the function called to generate a timestamp.
_TimestampFunc = partial(datetime.now, datetime.now().astimezone().tzinfo)

# _ExceptionHandler is called whenever zerolog fails to write an event on its
# output. If not set, an error is printed on the stderr. This handler must
# be thread safe and non-blocking.
_ExceptionHandler: Callable[[Exception], None] | None = None

# _LevelColors are used by ConsoleWriter's console_default_format_level to color
# log levels.
_LevelColors: Dict[Level, int] = {
    Level.TraceLevel: 34,  # blue
    Level.DebugLevel: 0,
    Level.InfoLevel: 32,  # green
    Level.WarnLevel: 33,  # yellow
    Level.ErrorLevel: 31,  # red
    Level.FatalLevel: 35,  # magenta
}

# _FormattedLevels are used by ConsoleWriter's console_default_format_level
# for a short level name.
_FormattedLevels: Dict[Level, str] = {
    Level.TraceLevel: "TRC",
    Level.DebugLevel: "DBG",
    Level.InfoLevel: "INF",
    Level.WarnLevel: "WRN",
    Level.ErrorLevel: "ERR",
    Level.FatalLevel: "FTL",
}

__g_level = Int(0)
__disable_sampling = Int(0)


# _set_global_level sets the global override for log level. If this
# values is raised, all Loggers will use at least this value.
#
# To globally disable logs, set global_level to Disabled.
def _set_global_level(lvl: Level):
    __g_level.store(lvl)


# _global_level returns the current global log level
def _global_level() -> Level:
    return Level(__g_level.load())


# _disable_sampling will disable sampling in all Loggers if true.
def _disable_sampling(v: bool):
    i = 0
    if v:
        i = 1
    __disable_sampling.store(i)


def _sampling_disabled() -> bool:
    return __disable_sampling.load() == 1
