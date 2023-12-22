import unittest
from dataclasses import dataclass

from zerolog import Level
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

        samplers = [
            TestCase("basic_sampler_1", BasicSampler(1), 100, 100, 100),
            TestCase("basic_sampler_5", BasicSampler(5), 100, 20, 20),
            TestCase("random_sampler", RandomSampler(5), 100, 10, 30),
            TestCase("burst_sampler", BurstSampler(20, 1), 100, 20, 20),
            TestCase(
                "burst_sampler_next", BurstSampler(20, 1, BasicSampler(5)), 120, 40, 40
            ),
        ]

        for s in samplers:
            got = 0
            for _ in range(s.total, 0, -1):
                if s.sampler.sample(Level.DebugLevel):
                    got += 1

            msg = f"{s.name}.sample(0) == true {got} on {s.total}, want [{s.want_min}, {s.want_max}]"
            self.assertFalse(got < s.want_min or got > s.want_max, msg)
