import json
from datetime import datetime
from inspect import Traceback
from typing import Any, Callable

from .constants import TimeFormatRFC3339Ms
from .internal.util.atomic import Int
from .level import Level

# TimestampFieldName is the field name used for the timestamp field.
_TimestampFieldName = "time"

# LevelFieldName is the field name used for the level field.
_LevelFieldName = "level"

# LevelTraceValue is the value used for the trace level field.
_LevelTraceValue = "trace"
# LevelDebugValue is the value used for the debug level field.
_LevelDebugValue = "debug"
# LevelInfoValue is the value used for the info level field.
_LevelInfoValue = "info"
# LevelWarnValue is the value used for the warn level field.
_LevelWarnValue = "warn"
# LevelErrorValue is the value used for the error level field.
_LevelErrorValue = "error"
# LevelFatalValue is the value used for the fatal level field.
_LevelFatalValue = "fatal"

# MessageFieldName is the field name used for the message field.
_MessageFieldName = "message"

# ExceptionFieldName is the field name used for exception fields.
_ExceptionFieldName = "exception"

# CallerFieldName is the field name used for caller field.
_CallerFieldName = "caller"

# CallerSkipFrameCount is the number of stack frames to skip to find the caller.
_CallerSkipFrameCount = 1


def _caller_marshal_func(tb: Traceback) -> str:
    return f"{tb.filename}:{tb.lineno}"


# CallerMarshalFunc allows customization of global caller marshaling
_CallerMarshalFunc = _caller_marshal_func

# ExceptionStackFieldName is the field name used for exception stacks.
_ExceptionStackFieldName = "stack"

# ExceptionStackMarshaler extract the stack from e if any.
_ExceptionStackMarshaler: Callable[[Exception], Any] | None = None


def _exception_marshal_func(e: Exception) -> Any:
    return e


# ExceptionMarshalFunc allows customization of global exception marshaling
_ExceptionMarshalFunc = _exception_marshal_func

# AnyMarshalFunc allows customization of any marshaling.
_AnyMarshalFunc = json.dumps

# TimeFieldFormat defines the time format of the time field type. If set to
# TimeFormatUnix, TimeFormatUnixMs or TimeFormatUnixMicro the time is formatted as a UNIX
# timestamp as integer. If set to TimeFormatRFC3339, TimeFormatRFC3339Ms or
# TimeFormatRFC3339Micro the time is formatted as a RFC3339 date string.
_TimeFieldFormat = TimeFormatRFC3339Ms

# TimestampFunc defines the function called to generate a timestamp.
_TimestampFunc = datetime.now

# ExceptionHandler is called whenever zerolog fails to write an event on its
# output. If not set, an error is printed on the stderr. This handler must
# be thread safe and non-blocking.
_ExceptionHandler: Callable[[Exception], None] | None = None

__g_level = Int(0)
__disable_sampling = Int(0)


# set_global_level sets the global override for log level. If this
# values is raised, all Loggers will use at least this value.
#
# To globally disable logs, set global_level to Disabled.
def _set_global_level(lvl: Level):
    __g_level.store(lvl)


# global_level returns the current global log level
def _global_level() -> Level:
    return Level(__g_level.load())


# disable_sampling will disable sampling in all Loggers if true.
def _disable_sampling(v: bool):
    i = 0
    if v:
        i = 1
    __disable_sampling.store(i)


def _sampling_disabled() -> bool:
    return __disable_sampling.load() == 1
