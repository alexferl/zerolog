from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .level import Level


# Sampler defines an interface to a log sampler.
class Sampler(Protocol):
    # Sample returns true if the event should be part of the sample, false if
    # the event should be dropped.
    @abstractmethod
    def sample(self, lvl: "Level") -> bool:
        pass
