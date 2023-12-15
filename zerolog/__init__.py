import sys

from ._globals import (
    _TimestampFieldName as TimestampFieldName,
    _LevelFieldName as LevelFieldName,
    _LevelTraceValue as LevelTraceValue,
    _LevelDebugValue as LevelDebugValue,
    _LevelInfoValue as LevelInfoValue,
    _LevelWarnValue as LevelWarnValue,
    _LevelErrorValue as LevelErrorValue,
    _LevelFatalValue as LevelFatalValue,
    _MessageFieldName as MessageFieldName,
    _ExceptionFieldName as ExceptionFieldName,
    _CallerFieldName as CallerFieldName,
    _CallerSkipFrameCount as CallerSkipFrameCount,
    _CallerMarshalFunc as CallerMarshalFunc,
    _ExceptionStackFieldName as ExceptionStackFieldName,
    _ExceptionStackMarshaler as ExceptionStackMarshaler,
    _ExceptionMarshalFunc as ExceptionMarshalFunc,
    _AnyMarshalFunc as AnyMarshalFunc,
    _TimeFieldFormat as TimeFieldFormat,
    _TimestampFunc as TimestampFunc,
    _ExceptionHandler as ExceptionHandler,
    _set_global_level as set_global_level,
    _global_level as global_level,
    _disable_sampling as disable_sampling,
    _sampling_disabled as sampling_disabled,
)
from .event import Event
from .level import Level
from .logger import Context, Hook, Logger, Sampler, new


# GlobalLogger is the global logger.
GlobalLogger = new(sys.stderr.buffer).ctx().timestamp().logger()
