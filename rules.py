from pathlib import Path
import yaml
from typing import Callable
from rule import Rule

RULES_FILE = Path(__file__).parent / "rules.yaml"

# Converts a string like 'has_alkene' into a function
def build_when(when_dict: dict) -> Callable[[dict], bool]:
    requires          = when_dict.get("requires", [])
    forbids           = when_dict.get("forbids", [])
    requires_any      = when_dict.get("requires_any", [])
    requires_two_plus = when_dict.get("requires_two_or_more", [])
 
    def when(wm: dict) -> bool:
        if requires and not all(wm.get(k, False) for k in requires):
            return False
        if forbids and any(wm.get(k, False) for k in forbids):
            return False
        if requires_any and not any(wm.get(k, False) for k in requires_any):
            return False
        if requires_two_plus and sum(bool(wm.get(k, False)) for k in requires_two_plus) < 2:
            return False
        return True
 
    return when
def load_rules() -> list[Rule]:
    with open(RULES_FILE, "r") as f:
        rule_data = yaml.safe_load(f)
    
    rules = []
    for entry in rule_data:
        rule = Rule(
            name=entry["name"],
            when=build_when(entry["when"]),
            conclusion=entry["conclusion"],
            priority=entry.get("priority", 0),
            explanation=entry.get("explanation", ""),
            retracts=entry.get("retracts", []),
            enabled=entry.get("enabled", True),
        )
        rules.append(rule)
    return rules


RULES: list[Rule] = load_rules()
