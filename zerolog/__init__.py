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
    _LevelColors as LevelColors,
    _FormattedLevels as FormattedLevels,
    _set_global_level as set_global_level,
    _global_level as global_level,
    _disable_sampling as disable_sampling,
    _sampling_disabled as sampling_disabled,
)
from .console import ConsoleWriter
from .constants import (
    TimeFormatRFC3339,
    TimeFormatRFC3339Ms,
    TimeFormatRFC3339Micro,
    TimeFormatUnix,
    TimeFormatUnixMs,
    TimeFormatUnixMicro,
)
from .context import Context
from .event import Event
from .hook import Hook, HookFunc, LevelHook
from .level import (
    Level,
    DebugLevel,
    InfoLevel,
    WarnLevel,
    ErrorLevel,
    FatalLevel,
    NoLevel,
    Disabled,
    TraceLevel,
)
from .logger import Logger, new
from .sampler import Sampler, BasicSampler, BurstSampler, LevelSampler, RandomSampler

# GlobalLogger is the global logger.
GlobalLogger = new(sys.stderr.buffer).ctx().timestamp().logger()
