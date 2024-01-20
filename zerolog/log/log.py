from typing import Any, IO

import zerolog


# output duplicates the global logger and sets w as its output.
def output(w: IO | Any) -> zerolog.Logger:
    return zerolog.GlobalLogger.output(w)


# ctx creates a child logger with the field added to its context.
def ctx() -> zerolog.Context:
    return zerolog.GlobalLogger.ctx()


# level creates a child logger with the minimum accepted level set to lvl.
def level(lvl: zerolog.Level) -> zerolog.Logger:
    return zerolog.GlobalLogger.level(lvl)


# sample returns a logger with the s sampler.
def sample(s: zerolog.Sampler) -> zerolog.Logger:
    return zerolog.GlobalLogger.sample(s)


# hook returns a logger with the h Hook.
def hook(h: zerolog.Hook) -> zerolog.Logger:
    return zerolog.GlobalLogger.hook(h)


# exc starts a new message with error level with e as a field.
#
# You must call msg on the returned event in order to send the event.
def exc(e) -> zerolog.Event | None:
    return zerolog.GlobalLogger.exc(e)


# trace starts a new message with trace level.
#
# You must call msg on the returned event in order to send the event.
def trace() -> zerolog.Event | None:
    return zerolog.GlobalLogger.trace()


# debug starts a new message with debug level.
#
# You must call msg on the returned event in order to send the event.
def debug() -> zerolog.Event | None:
    return zerolog.GlobalLogger.debug()


# info starts a new message with info level.
#
# You must call msg on the returned event in order to send the event.
def info() -> zerolog.Event | None:
    return zerolog.GlobalLogger.info()


# warn starts a new message with warn level.
#
# You must call msg on the returned event in order to send the event.
def warn() -> zerolog.Event | None:
    return zerolog.GlobalLogger.warn()


# error starts a new message with error level.
#
# You must call msg on the returned event in order to send the event.
def error() -> zerolog.Event | None:
    return zerolog.GlobalLogger.error()


# fatal starts a new message with fatal level. The sys.exit() function
# is called by the msg method.
#
# You must call msg on the returned event in order to send the event.
def fatal() -> zerolog.Event | None:
    return zerolog.GlobalLogger.fatal()


# with_level starts a new message with lvl.
#
# You must call msg on the returned event in order to send the event.
def with_level(lvl: zerolog.Level) -> zerolog.Event | None:
    return zerolog.GlobalLogger.with_level(lvl)


# log starts a new message with no level. Setting zerolog.GlobalLevel to
# zerolog.Disabled will still disable events produced by this method.
#
# You must call msg on the returned event in order to send the event.
def log() -> zerolog.Event | None:
    return zerolog.GlobalLogger.log()


# print sends a log event using debug level and no extra field.
def print(*args: Any):
    return zerolog.GlobalLogger.print(args)
