from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .event import Event
    from .level import Level


# Hook defines an interface to a log hook.
class Hook(Protocol):
    @abstractmethod
    def run(self, e: "Event", level: "Level", msg: str):
        pass
