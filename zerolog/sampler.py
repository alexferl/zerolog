import datetime
import random
from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from .internal.util.atomic import Int
from .level import Level


# Sampler defines an interface to a log sampler.
class Sampler(Protocol):
    # Sample returns true if the event should be part of the sample, false if
    # the event should be dropped.
    @abstractmethod
    def sample(self, lvl: Level) -> bool:
        pass


# RandomSampler use a PRNG to randomly sample an event out of n events,
# regardless of their level.
class RandomSampler:
    def __init__(self, n: int = 0):
        self._n = n

    def sample(self, lvl: Level) -> bool:
        if self._n <= 0:
            return False
        if random.randint(0, self._n) != 0:
            return False
        return True


# Often samples log every ~ 10 events.
Often = RandomSampler(10)
# Sometimes samples log every ~ 100 events.
Sometimes = RandomSampler(100)
# Rarely samples log every ~ 1000 events.
Rarely = RandomSampler(1000)


# BasicSampler is a sampler that will send every nth events, regardless of
# their level.
class BasicSampler:
    def __init__(self, n: int = 0):
        self.n = n
        self._counter = Int(0)

    def sample(self, lvl: Level) -> bool:
        n = self.n
        if n == 1:
            return True
        c = self._counter.add(1)
        return c % n == 1


# BurstSampler lets burst events pass per period then pass the decision to
# next_sampler. If sampler is not set, all subsequent events are rejected.
class BurstSampler:
    def __init__(
        self, burst: int = 0, period: int = 0, next_sampler: Sampler | None = None
    ):
        # burst is the maximum number of event per period allowed before calling
        # next_sampler.
        self.burst = burst
        # period defines the burst period. If 0, next_sampler is always called.
        self.period = period
        # next_sampler is the sampler used after the burst is reached. If None,
        # events are always rejected after the burst.
        self.next_sampler = next_sampler

        self._counter = Int(0)
        self._reset_at = Int(0)

    def sample(self, lvl: Level) -> bool:
        if self.burst > 0 and self.period > 0:
            if self._inc() <= self.burst:
                return True
        if self.next_sampler is None:
            return False
        return self.next_sampler.sample(lvl)

    def _inc(self) -> int:
        micro = 100000
        now = datetime.datetime.now().timestamp() * micro
        reset_at = self._reset_at.load()
        if now > reset_at:
            c = 1
            self._counter.store(c)
            new_reset_at = int(now + (self.period * micro))
            c = self._reset_at.compare_and_swap(reset_at, new_reset_at)
        else:
            c = self._counter.add(1)
        return c


# LevelSampler applies a different sampler for each level.
@dataclass
class LevelSampler:
    trace_sampler: Sampler | None = None
    debug_sampler: Sampler | None = None
    info_sampler: Sampler | None = None
    warn_sampler: Sampler | None = None
    error_sampler: Sampler | None = None

    def sample(self, lvl: Level) -> bool:
        match lvl:
            case lvl.TraceLevel:
                if self.trace_sampler is not None:
                    return self.trace_sampler.sample(lvl)
            case lvl.DebugLevel:
                if self.debug_sampler is not None:
                    return self.debug_sampler.sample(lvl)
            case lvl.InfoLevel:
                if self.info_sampler is not None:
                    return self.info_sampler.sample(lvl)
            case lvl.WarnLevel:
                if self.warn_sampler is not None:
                    return self.warn_sampler.sample(lvl)
            case lvl.ErrorLevel:
                if self.error_sampler is not None:
                    return self.error_sampler.sample(lvl)
        return True
