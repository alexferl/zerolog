import io
import unittest
from dataclasses import dataclass
from typing import Callable

import zerolog
from zerolog import Level, Logger
from zerolog.encoder_json import decode_if_binary_to_string
from zerolog.hook import HookFunc


level_name_hook = HookFunc(
    lambda e, level, msg: e.str(
        "level_name", level.string() if level != Level.NoLevel else "nolevel"
    )
)
simple_hook = HookFunc(
    lambda e, level, msg: (
        e.bool("has_level", level != Level.NoLevel),
        e.str("test", "logged"),
    )
)
copy_hook = HookFunc(
    lambda e, level, msg: (
        e.bool("copy_has_level", level != Level.NoLevel),
        e.str("copy_level", level.string()) if level != Level.NoLevel else None,
        e.str("copy_msg", msg),
    )
)
discard_hook = HookFunc(lambda e, level, message: e.discard())


class TestHook(unittest.TestCase):
    def test_hooks(self):
        @dataclass
        class TestCase:
            name: str
            want: str
            test: Callable[[Logger], None]

        tests = [
            TestCase(
                "Message",
                '{"level_name":"nolevel","message":"test message"}\n',
                lambda l: (log.hook(level_name_hook), log.log().msg("test message")),
            ),
            TestCase(
                "NoLevel",
                '{"level_name":"nolevel"}\n',
                lambda l: (log.hook(level_name_hook), log.log().msg("")),
            ),
            TestCase(
                "Print",
                '{"level":"debug","level_name":"debug"}\n',
                lambda l: (log.hook(level_name_hook), log.print("")),
            ),
            TestCase(
                "Error",
                '{"level":"error","level_name":"error"}\n',
                lambda l: (log.hook(level_name_hook), log.error().msg("")),
            ),
            TestCase(
                "Copy/1",
                '{"copy_has_level":false,"copy_msg":""}\n',
                lambda l: (log.hook(copy_hook), log.log().msg("")),
            ),
            TestCase(
                "Copy/2",
                '{"level":"info","copy_has_level":true,"copy_level":"info","copy_msg":"a message","message":"a message"}\n',
                lambda l: (log.hook(copy_hook), log.info().msg("a message")),
            ),
            TestCase(
                "Multi",
                '{"level":"error","level_name":"error","has_level":true,"test":"logged"}\n',
                lambda l: (
                    log.hook(level_name_hook).hook(simple_hook),
                    log.error().msg(""),
                ),
            ),
            TestCase(
                "Multi/Message",
                '{"level":"error","level_name":"error","has_level":true,"test":"logged","message":"a message"}\n',
                lambda l: (
                    log.hook(level_name_hook).hook(simple_hook),
                    log.error().msg("a message"),
                ),
            ),
            TestCase(
                "Output/single/pre",
                '{"level":"error","level_name":"error"}\n',
                lambda l: (
                    ignored := io.BytesIO(),
                    log := zerolog.new(ignored).hook(level_name_hook).output(l._w),
                    log.error().msg(""),
                ),
            ),
            TestCase(
                "Output/single/post",
                '{"level":"error","level_name":"error"}\n',
                lambda l: (
                    ignored := io.BytesIO(),
                    log := zerolog.new(ignored).output(l._w).hook(level_name_hook),
                    log.error().msg(""),
                ),
            ),
            TestCase(
                "Output/multi/pre",
                '{"level":"error","level_name":"error","has_level":true,"test":"logged"}\n',
                lambda l: (
                    ignored := io.BytesIO(),
                    log := zerolog.new(ignored)
                    .hook(level_name_hook)
                    .hook(simple_hook)
                    .output(l._w),
                    log.error().msg(""),
                ),
            ),
            TestCase(
                "Output/multi/post",
                '{"level":"error","level_name":"error","has_level":true,"test":"logged"}\n',
                lambda l: (
                    ignored := io.BytesIO(),
                    log := zerolog.new(ignored)
                    .output(l._w)
                    .hook(level_name_hook)
                    .hook(simple_hook),
                    log.error().msg(""),
                ),
            ),
            TestCase(
                "Output/mixed",
                '{"level":"error","level_name":"error","has_level":true,"test":"logged"}\n',
                lambda l: (
                    ignored := io.BytesIO(),
                    log := zerolog.new(ignored)
                    .hook(level_name_hook)
                    .output(l._w)
                    .hook(simple_hook),
                    log.error().msg(""),
                ),
            ),
            TestCase(
                "Ctx/single/pre",
                '{"level":"error","ctx":"pre","level_name":"error"}\n',
                lambda l: (
                    logger := log.hook(level_name_hook)
                    .ctx()
                    .str("ctx", "pre")
                    .logger(),
                    logger.error().msg(""),
                ),
            ),
            TestCase(
                "Ctx/single/post",
                '{"level":"error","ctx":"post","level_name":"error"}\n',
                lambda l: (
                    logger := log.ctx()
                    .str("ctx", "post")
                    .logger()
                    .hook(level_name_hook),
                    logger.error().msg(""),
                ),
            ),
            TestCase(
                "Ctx/multi/pre",
                '{"level":"error","ctx":"pre","level_name":"error","has_level":true,"test":"logged"}\n',
                lambda l: (
                    logger := log.hook(level_name_hook)
                    .hook(simple_hook)
                    .ctx()
                    .str("ctx", "pre")
                    .logger(),
                    logger.error().msg(""),
                ),
            ),
            TestCase(
                "Ctx/multi/post",
                '{"level":"error","ctx":"pre","level_name":"error","has_level":true,"test":"logged"}\n',
                lambda l: (
                    logger := log.ctx()
                    .str("ctx", "pre")
                    .logger()
                    .hook(level_name_hook)
                    .hook(simple_hook),
                    logger.error().msg(""),
                ),
            ),
            TestCase(
                "Ctx/mixed",
                '{"level":"error","ctx":"mixed","level_name":"error","has_level":true,"test":"logged"}\n',
                lambda l: (
                    logger := log.hook(level_name_hook)
                    .ctx()
                    .str("ctx", "mixed")
                    .logger()
                    .hook(simple_hook),
                    logger.error().msg(""),
                ),
            ),
            TestCase(
                "Discard",
                "",
                lambda l: (log.hook(discard_hook), log.log().msg("test message")),
            ),
            TestCase(
                "None",
                '{"level":"error"}\n',
                lambda l: (log.error().msg("")),
            ),
        ]

        for t in tests:
            out = io.BytesIO()
            log = zerolog.new(out)
            t.test(log)
            got = decode_if_binary_to_string(out.read())
            self.assertEqual(t.want, got)
