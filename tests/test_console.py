import datetime
import io
import os
import unittest
from typing import Any, Dict, IO

import zerolog
from zerolog import time


class TestConsoleLogger(unittest.TestCase):
    def test_numbers(self):
        buf = io.BytesIO()
        log = zerolog.new(zerolog.ConsoleWriter(out=buf, no_color=True))
        (
            log.info()
            .float("float", 1.23)
            .int("small", 123)
            .int("big", 1152921504606846976)
            .msg("msg")
        )
        got = buf.read().decode().strip()
        want = "None INF msg big=1152921504606846976 float=1.23 small=123"
        self.assertEqual(want, got)


class TestConsoleWriter(unittest.TestCase):
    def test_default_field_formatter(self):
        buf = io.BytesIO()
        w = zerolog.ConsoleWriter(out=buf, no_color=True, parts_order=["foo"])

        w.write(b'{"foo": "DEFAULT"}')

        want = "DEFAULT foo=DEFAULT\n"
        got = buf.read().decode()
        self.assertEqual(want, got)

    def test_write_colorized(self):
        buf = io.BytesIO()
        w = zerolog.ConsoleWriter(out=buf, no_color=False)

        w.write(b'{"level": "warn", "message": "Foobar"}')

        want = "\x1b[90mNone\x1b[0m \x1b[33mWRN\x1b[0m \x1b[1mFoobar\x1b[0m\n"
        got = buf.read().decode()
        self.assertEqual(want, got)

    def test_no_color_true(self):
        os.environ["NO_COLOR"] = "anything"

        buf = io.BytesIO()
        w = zerolog.ConsoleWriter(out=buf)

        w.write(b'{"level": "warn", "message": "Foobar"}')

        want = "None WRN Foobar\n"
        got = buf.read().decode()
        self.assertEqual(want, got)

        del os.environ["NO_COLOR"]

    def test_write_fields(self):
        buf = io.BytesIO()
        w = zerolog.ConsoleWriter(out=buf, no_color=True)

        d = datetime.datetime.fromtimestamp(0, datetime.UTC)
        w.write(
            f'{{"time": "{d}", "level": "debug", "message": "Foobar", "foo": "bar"}}'.encode()
        )

        want = f"{d.strftime(time.Kitchen)} DBG Foobar foo=bar\n"
        got = buf.read().decode()
        self.assertEqual(want, got)

    def test_unix_timestamp_input_format(self):
        of = zerolog.TimeFieldFormat
        try:
            zerolog.TimeFieldFormat = zerolog.TimeFormatUnix

            buf = io.BytesIO()
            w = zerolog.ConsoleWriter(
                out=buf, time_format=time.StampMicro, no_color=True
            )

            w.write(
                b'{"time": 1234, "level": "debug", "message": "Foobar", "foo": "bar"}'
            )

            ts = datetime.datetime.fromtimestamp(1234).strftime(time.StampMicro)
            want = f"{ts} DBG Foobar foo=bar\n"
            got = buf.read().decode()
            self.assertEqual(want, got)
        finally:
            zerolog.TimeFieldFormat = of

    def test_no_message_field(self):
        buf = io.BytesIO()
        w = zerolog.ConsoleWriter(out=buf, no_color=True)

        w.write(b'{"level": "debug", "foo": "bar"}')

        want = f"None DBG foo=bar\n"
        got = buf.read().decode()
        self.assertEqual(want, got)

    def test_no_level_field(self):
        buf = io.BytesIO()
        w = zerolog.ConsoleWriter(out=buf, no_color=True)

        w.write(b'{"message": "Foobar", "foo": "bar"}')

        want = f"None ??? Foobar foo=bar\n"
        got = buf.read().decode()
        self.assertEqual(want, got)

    def test_write_colorized_fields(self):
        buf = io.BytesIO()
        w = zerolog.ConsoleWriter(out=buf, no_color=False)

        w.write(b'{"level": "warn", "message": "Foobar", "foo": "bar"}')

        want = f"\x1b[90mNone\x1b[0m \x1b[33mWRN\x1b[0m \x1b[1mFoobar\x1b[0m \x1b[36mfoo=\x1b[0mbar\n"
        got = buf.read().decode()
        self.assertEqual(want, got)

    def test_write_exception_field(self):
        buf = io.BytesIO()
        w = zerolog.ConsoleWriter(out=buf, no_color=True)

        ts = datetime.datetime.fromtimestamp(0, datetime.UTC)
        d = ts.strftime(time.RFC3339)
        w.write(
            f'{{"time": "{d}", "level": "error", "message": "Foobar", "aaa": "bbb", "exception": "Exception"}}'.encode()
        )

        want = f"{ts.strftime(time.Kitchen)} ERR Foobar exception=Exception aaa=bbb\n"
        got = buf.read().decode()
        self.assertEqual(want, got)

    def test_write_caller_field(self):
        buf = io.BytesIO()
        w = zerolog.ConsoleWriter(out=buf, no_color=True)

        cwd = os.getcwd()
        path = cwd + "/foo/bar.py"

        ts = datetime.datetime.fromtimestamp(0, datetime.UTC)
        d = ts.strftime(time.RFC3339)
        w.write(
            f'{{"time": "{d}", "level": "debug", "message": "Foobar", "foo": "bar", "caller": "{path}"}}'.encode()
        )

        want = f"{ts.strftime(time.Kitchen)} DBG foo/bar.py > Foobar foo=bar\n"
        got = buf.read().decode()
        self.assertEqual(want, got)

    def test_write_json_field(self):
        buf = io.BytesIO()
        w = zerolog.ConsoleWriter(out=buf, no_color=True)

        w.write(
            '{"level": "debug", "message": "Foobar", "foo": [1, 2, 3], "bar": true}'.encode()
        )

        want = f"None DBG Foobar bar=True foo=[1, 2, 3]\n"
        got = buf.read().decode()
        self.assertEqual(want, got)


class TestConsoleWriterConfig(unittest.TestCase):
    def test_set_time_format(self):
        buf = io.BytesIO()
        w = zerolog.ConsoleWriter(out=buf, no_color=True)

        ts = datetime.datetime.fromtimestamp(0, datetime.UTC)
        d = ts.strftime(time.RFC3339)
        w.write(f'{{"time": "{d}", "level": "info", "message": "Foobar"}}'.encode())

        want = f"{ts.strftime(time.Kitchen)} INF Foobar\n"
        got = buf.read().decode()
        self.assertEqual(want, got)

    def test_set_parts_order(self):
        buf = io.BytesIO()
        w = zerolog.ConsoleWriter(
            out=buf, no_color=True, parts_order=["message", "level"]
        )

        w.write('{"level": "info", "message": "Foobar"}'.encode())

        want = f"Foobar INF\n"
        got = buf.read().decode()
        self.assertEqual(want, got)

    def test_set_parts_exclude(self):
        buf = io.BytesIO()
        w = zerolog.ConsoleWriter(out=buf, no_color=True, parts_exclude=["time"])

        ts = datetime.datetime.fromtimestamp(0, datetime.UTC)
        d = ts.strftime(time.RFC3339)
        w.write(f'{{"time": "{d}", "level": "info", "message": "Foobar"}}'.encode())

        want = f"INF Foobar\n"
        got = buf.read().decode()
        self.assertEqual(want, got)

    def test_set_fields_exclude(self):
        buf = io.BytesIO()
        w = zerolog.ConsoleWriter(out=buf, no_color=True, fields_exclude=["foo"])

        w.write(
            '{"level": "info", "message": "Foobar", "foo": "bar", "baz": "quux"}'.encode()
        )

        want = f"None INF Foobar baz=quux\n"
        got = buf.read().decode()
        self.assertEqual(want, got)

    def test_set_format_extra(self):
        def format_extra(evt: Dict[str, Any], buf: IO):
            buf.write(b"\nAdditional stacktrace")

        buf = io.BytesIO()
        w = zerolog.ConsoleWriter(
            out=buf,
            no_color=True,
            parts_order=["level", "message"],
            format_extra=format_extra,
        )

        w.write('{"level": "info", "message": "Foobar"}'.encode())

        want = f"INF Foobar\nAdditional stacktrace\n"
        got = buf.read().decode()
        self.assertEqual(want, got)

    def test_set_format_prepare(self):
        def format_prepare(evt: Dict[str, Any]):
            evt["message"] = f'msg={evt["message"]}'

        buf = io.BytesIO()
        w = zerolog.ConsoleWriter(
            out=buf,
            no_color=True,
            parts_order=["level", "message"],
            format_prepare=format_prepare,
        )

        w.write('{"level": "info", "message": "Foobar"}'.encode())

        want = f"INF msg=Foobar\n"
        got = buf.read().decode()
        self.assertEqual(want, got)
