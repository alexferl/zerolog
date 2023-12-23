import datetime
import unittest
from dataclasses import dataclass

from zerolog import Level, log
from zerolog.sampler import Sampler, BasicSampler, BurstSampler, RandomSampler


class TestSampler(unittest.TestCase):
    def test_samplers(self):
        @dataclass
        class TestCase:
            name: str
            sampler: Sampler
            total: int
            want_min: int
            want_max: int

        tests = [
            TestCase("basic_sampler_1", BasicSampler(1), 100, 100, 100),
            TestCase("basic_sampler_5", BasicSampler(5), 100, 20, 20),
            TestCase("random_sampler", RandomSampler(5), 100, 10, 30),
            TestCase("burst_sampler", BurstSampler(20, 1), 100, 20, 20),
            TestCase(
                "burst_sampler_next", BurstSampler(20, 1, BasicSampler(5)), 120, 40, 40
            ),
        ]

        for t in tests:
            got = 0
            for _ in range(t.total, 0, -1):
                if t.sampler.sample(Level.DebugLevel):
                    got += 1

            msg = f"{t.name}.sample(0) == true {got} on {t.total}, want [{t.want_min}, {t.want_max}]"
            self.assertFalse(got < t.want_min or got > t.want_max, msg)
