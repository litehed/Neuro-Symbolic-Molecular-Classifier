from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Rule:
    name: str
    when: Callable[[dict], bool]
    conclusion: str
    priority: int
    explanation: str
    # prevents mutable default I guess
    retracts: list[str] = field(default_factory=list)
    enabled: bool = True

    # True if prediction holds and is enabled
    def fires(self, working_memory: dict) -> bool:
        return self.enabled and self.when(working_memory)