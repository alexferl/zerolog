import datetime
import io
import unittest
from dataclasses import dataclass

import zerolog
from zerolog import stacktrace
from zerolog.encoder_json import decode_if_binary_to_string


class TestLog(unittest.TestCase):
    def test_empty(self):
        out = io.BytesIO()
        log = zerolog.new(out)
        log.log().msg("")
        got = decode_if_binary_to_string(out.read())
        want = "{}\n"
        self.assertEqual(want, got)

    def test_one_field(self):
        out = io.BytesIO()
        log = zerolog.new(out)
        log.log().str("foo", "bar").msg("")
        got = decode_if_binary_to_string(out.read())
        want = '{"foo":"bar"}\n'
        self.assertEqual(want, got)

    def test_one_field_list(self):
        out = io.BytesIO()
        log = zerolog.new(out)
        log.log().strs("foo", ["bar"]).msg("")
        got = decode_if_binary_to_string(out.read())
        want = '{"foo":["bar"]}\n'
        self.assertEqual(want, got)

    def test_two_field(self):
        out = io.BytesIO()
        log = zerolog.new(out)
        log.log().str("foo", "bar").int("n", 123).msg("")
        got = decode_if_binary_to_string(out.read())
        want = '{"foo":"bar","n":123}\n'
        self.assertEqual(want, got)

    def test_two_field_list(self):
        out = io.BytesIO()
        log = zerolog.new(out)
        log.log().strs("foo", ["bar"]).ints("n", [123]).msg("")
        got = decode_if_binary_to_string(out.read())
        want = '{"foo":["bar"],"n":[123]}\n'
        self.assertEqual(want, got)

    def test_standard_fields(self):
        out = io.BytesIO()
        log = zerolog.new(out)
        log.log().str("foo", "bar").int("n", 123).float("f", 1.23).bool(
            "b", True
        ).send()
        got = decode_if_binary_to_string(out.read())
        want = '{"foo":"bar","n":123,"f":1.23,"b":true}\n'
        self.assertEqual(want, got)

    def test_standard_fields_lists(self):
        out = io.BytesIO()
        log = zerolog.new(out)
        log.log().strs("foo", ["bar", "quux"]).ints("n", [123, 456]).floats(
            "f", [1.23, 4.56]
        ).bools("b", [True, False]).send()
        got = decode_if_binary_to_string(out.read())
        want = '{"foo":["bar","quux"],"n":[123,456],"f":[1.23,4.56],"b":[true,false]}\n'
        self.assertEqual(want, got)

    def test_standard_fields_empty_lists(self):
        out = io.BytesIO()
        log = zerolog.new(out)
        log.log().strs("foo", []).ints("n", []).floats("f", []).bools("b", []).send()
        got = decode_if_binary_to_string(out.read())
        want = '{"foo":[],"n":[],"f":[],"b":[]}\n'
        self.assertEqual(want, got)

    def test_time_rfc3339(self):
        of = zerolog.TimeFieldFormat
        try:

            @dataclass
            class TestCase:
                fmt: str
                out: str

            tests = [
                TestCase(zerolog.TimeFormatRFC3339, "2006-01-02T00:00:00Z"),
                TestCase(zerolog.TimeFormatRFC3339Ms, "2006-01-02T00:00:00.000Z"),
                TestCase(zerolog.TimeFormatRFC3339Micro, "2006-01-02T00:00:00.000000Z"),
            ]

            for t in tests:
                zerolog.TimeFieldFormat = t.fmt
                out = io.BytesIO()
                log = zerolog.new(out)
                log.log().time(
                    "dt", datetime.datetime(2006, 1, 2, tzinfo=datetime.UTC)
                ).send()
                got = decode_if_binary_to_string(out.read())
                want = f'{{"dt":"{t.out}"}}\n'
                self.assertEqual(want, got)
        finally:
            zerolog.TimeFieldFormat = of

    def test_time_unix(self):
        of = zerolog.TimeFieldFormat
        try:

            @dataclass
            class TestCase:
                fmt: str
                out: int

            tests = [
                TestCase(zerolog.TimeFormatUnix, 1136160000),
                TestCase(zerolog.TimeFormatUnixMs, 1136160000000),
                TestCase(zerolog.TimeFormatUnixMicro, 1136160000000000),
            ]

            for t in tests:
                zerolog.TimeFieldFormat = t.fmt
                out = io.BytesIO()
                log = zerolog.new(out)
                log.log().time(
                    "dt", datetime.datetime(2006, 1, 2, tzinfo=datetime.UTC)
                ).send()
                got = decode_if_binary_to_string(out.read())
                want = f'{{"dt":{t.out}}}\n'
                self.assertEqual(want, got)
        finally:
            zerolog.TimeFieldFormat = of

    def test_time_custom_format(self):
        of = zerolog.TimeFieldFormat
        try:
            zerolog.TimeFieldFormat = "%Y/%m/%d"
            out = io.BytesIO()
            log = zerolog.new(out)
            log.log().time(
                "dt", datetime.datetime(2006, 1, 2, tzinfo=datetime.UTC)
            ).send()
            got = decode_if_binary_to_string(out.read())
            want = '{"dt":"2006/01/02"}\n'
            self.assertEqual(want, got)
        finally:
            zerolog.TimeFieldFormat = of

    def test_level(self):
        out = io.BytesIO()
        log = zerolog.new(out)
        logger = log.level(zerolog.WarnLevel)
        self.assertIsNone(logger.info())
        logger.warn().str("foo", "bar").msg("")
        got = decode_if_binary_to_string(out.read())
        want = '{"level":"warn","foo":"bar"}\n'
        self.assertEqual(want, got)

    def test_get_level(self):
        out = io.BytesIO()
        log = zerolog.new(out)
        logger = log.level(zerolog.WarnLevel)
        self.assertEqual(zerolog.WarnLevel, logger.get_level())

    def test_with_level(self):
        for level in [
            zerolog.DebugLevel,
            zerolog.InfoLevel,
            zerolog.WarnLevel,
            zerolog.ErrorLevel,
            zerolog.FatalLevel,
        ]:
            out = io.BytesIO()
            log = zerolog.new(out)
            log.with_level(level).str("foo", "bar").msg("")
            got = decode_if_binary_to_string(out.read())
            want = f'{{"level":"{level.string()}","foo":"bar"}}\n'
            self.assertEqual(want, got)

    def test_exception(self):
        out = io.BytesIO()
        log = zerolog.new(out)
        log.log().exc(Exception("my exception")).send()
        got = decode_if_binary_to_string(out.read())
        want = '{"exception":"my exception"}\n'
        self.assertEqual(want, got)

    def test_exception_stack_marshaler_not_set(self):
        out = io.BytesIO()
        log = zerolog.new(out)
        log.log().stack().exc(Exception("my exception")).send()
        got = decode_if_binary_to_string(out.read())
        want = '{"exception":"my exception"}\n'
        self.assertEqual(want, got)

    def test_exception_stack(self):
        of = zerolog.ExceptionStackMarshaler
        try:
            zerolog.ExceptionStackMarshaler = stacktrace.marshal_stack
            out = io.BytesIO()
            log = zerolog.new(out)
            log.log().stack().exc(Exception("my exception")).send()
            got = decode_if_binary_to_string(out.read())
            want = '{"stack":[],"exception":"my exception"}\n'
            self.assertEqual(want, got)
        finally:
            zerolog.ExceptionStackMarshaler = of


class TestInfo(unittest.TestCase):
    def test_empty(self):
        out = io.BytesIO()
        log = zerolog.new(out)
        log.info().msg("")
        got = decode_if_binary_to_string(out.read())
        want = '{"level":"info"}\n'
        self.assertEqual(want, got)

    def test_one_field(self):
        out = io.BytesIO()
        log = zerolog.new(out)
        log.info().str("foo", "bar").msg("")
        got = decode_if_binary_to_string(out.read())
        want = '{"level":"info","foo":"bar"}\n'
        self.assertEqual(want, got)

    def test_one_field_list(self):
        out = io.BytesIO()
        log = zerolog.new(out)
        log.info().strs("foo", ["bar"]).msg("")
        got = decode_if_binary_to_string(out.read())
        want = '{"level":"info","foo":["bar"]}\n'
        self.assertEqual(want, got)

    def test_two_field(self):
        out = io.BytesIO()
        log = zerolog.new(out)
        log.info().str("foo", "bar").int("n", 123).msg("")
        got = decode_if_binary_to_string(out.read())
        want = '{"level":"info","foo":"bar","n":123}\n'
        self.assertEqual(want, got)

    def test_two_field_list(self):
        out = io.BytesIO()
        log = zerolog.new(out)
        log.info().strs("foo", ["bar"]).ints("n", [123]).msg("")
        got = decode_if_binary_to_string(out.read())
        want = '{"level":"info","foo":["bar"],"n":[123]}\n'
        self.assertEqual(want, got)


class TestEmptyLevelFieldName(unittest.TestCase):
    field_name = zerolog.LevelFieldName

    def setUp(self):
        zerolog.LevelFieldName = ""

    def tearDown(self):
        zerolog.LevelFieldName = self.field_name

    def test_empty_setting(self):
        out = io.BytesIO()
        log = zerolog.new(out)
        log.info().str("foo", "bar").int("n", 123).msg("")
        got = decode_if_binary_to_string(out.read())
        want = '{"foo":"bar","n":123}\n'
        self.assertEqual(want, got)
