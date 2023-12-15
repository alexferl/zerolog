import io
import unittest

import zerolog
from zerolog.encoder_json import decode_if_binary_to_string


class TestLog(unittest.TestCase):
    def test_empty(self):
        out = io.BytesIO()
        log = zerolog.new(out)
        log.log().msg("")
        got = decode_if_binary_to_string(out.read())
        want = "{}\n"
        self.assertEqual(got, want)

    def test_one_field(self):
        out = io.BytesIO()
        log = zerolog.new(out)
        log.log().str("foo", "bar").msg("")
        got = decode_if_binary_to_string(out.read())
        want = '{"foo":"bar"}\n'
        self.assertEqual(got, want)

    def test_two_field(self):
        out = io.BytesIO()
        log = zerolog.new(out)
        log.log().str("foo", "bar").int("n", 123).msg("")
        got = decode_if_binary_to_string(out.read())
        want = '{"foo":"bar","n":123}\n'
        self.assertEqual(got, want)


class TestInfo(unittest.TestCase):
    def test_empty(self):
        out = io.BytesIO()
        log = zerolog.new(out)
        log.info().msg("")
        got = decode_if_binary_to_string(out.read())
        want = '{"level":"info"}\n'
        self.assertEqual(got, want)

    def test_one_field(self):
        out = io.BytesIO()
        log = zerolog.new(out)
        log.info().str("foo", "bar").msg("")
        got = decode_if_binary_to_string(out.read())
        want = '{"level":"info","foo":"bar"}\n'
        self.assertEqual(got, want)

    def test_two_field(self):
        out = io.BytesIO()
        log = zerolog.new(out)
        log.info().str("foo", "bar").int("n", 123).msg("")
        got = decode_if_binary_to_string(out.read())
        want = '{"level":"info","foo":"bar","n":123}\n'
        self.assertEqual(got, want)


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
        self.assertEqual(got, want)
