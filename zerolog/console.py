import enum
import json
import os
import sys
from datetime import datetime
from typing import Any, Callable, Dict, IO, List

from dateutil.parser import parse

import zerolog
from zerolog import constants, time
from .internal.util.time import convert_offset
from .level import parse_level


class Colors(enum.IntEnum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37

    BOLD = 1
    DARK_GRAY = 90


# Formatter transforms the input into a formatted string.
Formatter = Callable[[Any], str]

_console_default_time_format = time.Kitchen


# ConsoleWriter parses the JSON input and writes it in an
# (optionally) colorized, human-friendly format to out.
class ConsoleWriter:
    def __init__(
        self,
        out: IO = sys.stdout.buffer,
        no_color: bool = False,
        time_format: str = _console_default_time_format,
        parts_order: List[str] | None = None,
        parts_exclude: List[str] | None = None,
        fields_exclude: List[str] | None = None,
        format_timestamp: Formatter | None = None,
        format_level: Formatter | None = None,
        format_caller: Formatter | None = None,
        format_message: Formatter | None = None,
        format_field_name: Formatter | None = None,
        format_field_value: Formatter | None = None,
        format_exc_field_name: Formatter | None = None,
        format_exc_field_value: Formatter | None = None,
        format_extra: Callable[[Dict[str, Any], IO], None] | None = None,
        format_prepare: Callable[[Dict[str, Any]], None] | None = None,
    ):
        # out is the output destination.
        self.out = out
        # no_color disables the colorized output.
        self.no_color = no_color
        # time_format specifies the format for timestamp in output.
        self.time_format = time_format
        # parts_order defines the order of parts in output.
        self.parts_order = parts_order or console_default_parts_order()
        # parts_exclude defines parts to not display in output.
        self.parts_exclude = parts_exclude or []
        # fields_exclude defines contextual fields to not display in output.
        self.fields_exclude = fields_exclude or []
        self.format_timestamp = format_timestamp
        self.format_level = format_level
        self.format_caller = format_caller
        self.format_message = format_message
        self.format_field_name = format_field_name
        self.format_field_value = format_field_value
        self.format_exc_field_name = format_exc_field_name
        self.format_exc_field_value = format_exc_field_value
        self.format_extra = format_extra
        self.format_prepare = format_prepare
        self._wrote_first_part = False

    # write transforms the JSON input with formatters and appends to self.out.
    def write(self, p: bytes) -> int:
        if len(self.parts_order) == 0:
            self.parts_order = console_default_parts_order()

        evt = json.loads(p)

        if self.format_prepare is not None:
            self.format_prepare(evt)

        for part in self.parts_order:
            self._write_part(self.out, evt, part)

        self._write_fields(evt, self.out)

        if self.format_extra is not None:
            self.format_extra(evt, self.out)

        self.out.write(b"\n")
        if hasattr(self.out, "seek"):
            self.out.seek(0)

        self._wrote_first_part = False

        return len(p)

    # _write_fields appends formatted key-value pairs to buf.
    def _write_fields(self, evt: Dict[str, Any], buf: IO):
        fields = []
        for field in evt.keys():
            is_excluded = False
            for excluded in self.fields_exclude:
                if field == excluded:
                    is_excluded = True
                    break
            if is_excluded:
                continue

            match field:
                case zerolog.LevelFieldName | zerolog.TimestampFieldName | zerolog.MessageFieldName | zerolog.CallerFieldName:
                    continue
            fields.append(field)

        fields = sorted(fields)

        if len(fields) > 0:
            buf.write(b" ")

        # Move the "exception" field to the front
        try:
            ei = fields.index(zerolog.ExceptionFieldName)
            if ei < len(fields) and fields[ei] == zerolog.ExceptionFieldName:
                fields.insert(0, fields.pop(ei))
        except ValueError:
            pass

        for i, field in enumerate(fields):
            if field == zerolog.ExceptionFieldName:
                if self.format_exc_field_name is None:
                    fn = console_default_format_exc_field_name(self.no_color)
                else:
                    fn = self.format_exc_field_name
                if self.format_exc_field_value is None:
                    fv = console_default_format_exc_field_value(self.no_color)
                else:
                    fv = self.format_exc_field_value
            else:
                if self.format_field_name is None:
                    fn = console_default_format_field_name(self.no_color)
                else:
                    fn = self.format_field_name
                if self.format_field_value is None:
                    fv = console_default_format_field_value
                else:
                    fv = self.format_field_value

            buf.write(fn(field).encode())

            match val := evt[field]:
                case str():
                    if needs_quote(val):
                        # TODO: escape?
                        buf.write(fv(val).encode())
                    else:
                        buf.write(fv(val).encode())
                case int():
                    buf.write(fv(val).encode())
                case _:
                    try:
                        b = zerolog.AnyMarshalFunc(val)
                        buf.write(fv(b).encode())
                    except Exception as e:
                        buf.write(
                            _colorize("[error: %v]", Colors.RED, self.no_color).encode()
                        )

            if i < len(fields) - 1:  # Skip space for last field
                buf.write(b" ")

    # _write_part appends a formatted part to buf.
    def _write_part(self, buf: IO, evt: Dict[str, Any], p: str):
        if len(self.parts_exclude) > 0:
            for exclude in self.parts_exclude:
                if exclude == p:
                    return

        match p:
            case zerolog.LevelFieldName:
                if self.format_level is None:
                    f = console_default_format_level(self.no_color)
                else:
                    f = self.format_level
            case zerolog.TimestampFieldName:
                if self.format_timestamp is None:
                    f = _console_default_format_timestamp(
                        self.time_format, self.no_color
                    )
                else:
                    f = self.format_timestamp
            case zerolog.MessageFieldName:
                if self.format_message is None:
                    f = console_default_format_message(
                        self.no_color, evt.get(zerolog.LevelFieldName)
                    )
                else:
                    f = self.format_message
            case zerolog.CallerFieldName:
                if self.format_caller is None:
                    f = console_default_format_caller(self.no_color)
                else:
                    f = self.format_caller
            case _:
                if self.format_field_value is None:
                    f = console_default_format_field_value
                else:
                    f = self.format_field_value

        s = f(evt.get(p, None))
        if s is not None and len(s) > 0:
            if self._wrote_first_part is True:
                buf.write(b" ")  # // write space only if not the first part
            buf.write(s.encode())
            if self._wrote_first_part is False:
                self._wrote_first_part = True


# needs_quote returns true when the string s should be quoted in output.
def needs_quote(s: str) -> bool:
    for i, _ in enumerate(s):
        if s[i] < "\x20" or s[i] > "\x7e" or s[i] == " " or s[i] == "\\" or s[i] == '"':
            return True
    return False


# _colorize returns the string s wrapped in ANSI code c, unless disabled is true or c is 0.
def _colorize(s: Any, c: int, disabled: bool) -> str:
    e = os.getenv("NO_COLOR")
    if e is not None or c == 0:
        disabled = True

    if disabled:
        return f"{s}"

    return f"\x1b[{c}m{s}\x1b[0m"


def console_default_parts_order() -> List[str]:
    return [
        zerolog.TimestampFieldName,
        zerolog.LevelFieldName,
        zerolog.CallerFieldName,
        zerolog.MessageFieldName,
    ]


def _console_default_format_timestamp(time_format: str, no_color: bool) -> Formatter:
    if time_format == "":
        time_format = _console_default_time_format

    def fn(i: Any) -> str:
        t = "None"
        match i:
            case str():
                tt = parse(i)
                match time_format:
                    case zerolog.TimeFormatRFC3339:
                        t = convert_offset(tt.isoformat(timespec="seconds"))
                    case zerolog.TimeFormatRFC3339Ms:
                        t = convert_offset(tt.isoformat(timespec="milliseconds"))
                    case zerolog.TimeFormatRFC3339Micro:
                        t = convert_offset(tt.isoformat(timespec="microseconds"))
                    case _:
                        t = tt.strftime(time_format)
            case int():
                match zerolog.TimeFieldFormat:
                    case constants.TimeFormatUnixMs:
                        i = i / 1000
                    case constants.TimeFormatUnixMicro:
                        i = i / 1000000
                t = datetime.fromtimestamp(i).strftime(time_format)

        return _colorize(t, Colors.DARK_GRAY, no_color)

    return fn


def console_default_format_level(no_color: bool) -> Formatter:
    def fn(i: Any) -> str:
        match i:
            case str():
                level = parse_level(i)
                try:
                    fl = zerolog.FormattedLevels[level]
                    l = _colorize(fl, zerolog.LevelColors[level], no_color)
                except KeyError:
                    l = i.upper()[0:3]
            case _:
                if i is None:
                    l = "???"
                else:
                    l = i.upper()[0:3]
        return l

    return fn


def console_default_format_caller(no_color: bool) -> Formatter:
    def fn(i: Any) -> str:
        if i is not None and len(i) > 0:
            rel = os.path.relpath(i, os.getcwd())
            i = _colorize(rel, Colors.BOLD, no_color) + _colorize(
                " >", Colors.CYAN, no_color
            )
        return i

    return fn


def console_default_format_message(no_color: bool, level: Any) -> Formatter:
    def fn(i: Any) -> str:
        if i is None or i == "":
            return ""
        match level:
            case zerolog.LevelInfoValue | zerolog.LevelWarnValue | zerolog.LevelErrorValue | zerolog.LevelFatalValue:
                return _colorize(f"{i}", Colors.BOLD, no_color)
            case _:
                return f"{i}"

    return fn


def console_default_format_field_name(no_color: bool) -> Formatter:
    def fn(i: Any) -> str:
        return _colorize(f"{i}=", Colors.CYAN, no_color)

    return fn


def console_default_format_field_value(i: Any) -> str:
    return f"{i}"


def console_default_format_exc_field_name(no_color: bool) -> Formatter:
    def fn(i: Any) -> str:
        return _colorize(f"{i}=", Colors.CYAN, no_color)

    return fn


def console_default_format_exc_field_value(no_color: bool) -> Formatter:
    def fn(i: Any) -> str:
        return _colorize(_colorize(f"{i}", Colors.BOLD, no_color), Colors.RED, no_color)

    return fn
