import unittest
from dataclasses import dataclass

from zerolog.encoder_json import enc


class TestEncoder(unittest.TestCase):
    def test_append_string(self):
        @dataclass
        class TestCase:
            inp: str
            out: str

        tests = [
            TestCase("", '""'),
            TestCase("\\", '"\\\\"'),
            TestCase("\x00", '"\\u0000"'),
            TestCase("\x01", '"\\u0001"'),
            TestCase("\x02", '"\\u0002"'),
            TestCase("\x03", '"\\u0003"'),
            TestCase("\x04", '"\\u0004"'),
            TestCase("\x05", '"\\u0005"'),
            TestCase("\x06", '"\\u0006"'),
            TestCase("\x07", '"\\u0007"'),
            TestCase("\x08", '"\\b"'),
            TestCase("\x09", '"\\t"'),
            TestCase("\x0a", '"\\n"'),
            TestCase("\x0b", '"\\u000b"'),
            TestCase("\x0c", '"\\f"'),
            TestCase("\x0d", '"\\r"'),
            TestCase("\x0e", '"\\u000e"'),
            TestCase("\x0f", '"\\u000f"'),
            TestCase("\x10", '"\\u0010"'),
            TestCase("\x11", '"\\u0011"'),
            TestCase("\x12", '"\\u0012"'),
            TestCase("\x13", '"\\u0013"'),
            TestCase("\x14", '"\\u0014"'),
            TestCase("\x15", '"\\u0015"'),
            TestCase("\x16", '"\\u0016"'),
            TestCase("\x17", '"\\u0017"'),
            TestCase("\x18", '"\\u0018"'),
            TestCase("\x19", '"\\u0019"'),
            TestCase("\x1a", '"\\u001a"'),
            TestCase("\x1b", '"\\u001b"'),
            TestCase("\x1c", '"\\u001c"'),
            TestCase("\x1d", '"\\u001d"'),
            TestCase("\x1e", '"\\u001e"'),
            TestCase("\x1f", '"\\u001f"'),
            TestCase("✭", '"✭"'),
            TestCase("foo\xc2\x7fbar", '"fooÂ\u007fbar"'),  # invalid sequence
            TestCase("ascii", '"ascii"'),
            TestCase('"a', '"\\"a"'),
            TestCase('foo"bar"baz', '"foo\\"bar\\"baz"'),
            TestCase("\x1ffoo\x1fbar\x1fbaz", '"\\u001ffoo\\u001fbar\\u001fbaz"'),
            TestCase("emoji \u2764\ufe0f!", '"emoji ❤️!"'),
        ]

        for t in tests:
            b = enc.append_string(b"", t.inp)
            got = b.decode()
            want = t.out
            self.assertEqual(want, got)
