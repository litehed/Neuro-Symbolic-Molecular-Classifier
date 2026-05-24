from dataclasses import dataclass

from rules import Rule


@dataclass
class Trace:
    rule_name: str
    explanation: str
    evidence: dict[str, list[str]]
    conclusion: str
    retracted: list[str]
    iteration: int


class InferenceEngine:
    def __init__(self, rules: list[Rule]):
        self.rules = sorted(rules, key=lambda r: r.priority, reverse=True)

    def infer(self, initial_working_memory: dict) -> tuple[list[Rule], dict, list[Trace]]:
        working_memory = initial_working_memory.copy()
        fired_names = set()
        fired_rules = []
        trace = []
        i = 0

        while True:
            conflict_set = [rule for rule in self.rules if rule.fires(
                working_memory) and rule.name not in fired_names]
            if not conflict_set:
                break

            i += 1

            selected = conflict_set[0]  # highest priority

            true_keys = [k for k, v in working_memory.items() if v is True]
            evidence = {
                "facts": [k for k in true_keys if k.startswith("has_")],
                "conclusions": [k for k in true_keys if not k.startswith("has_")
                                and k not in ("num_atoms", "num_bonds")],
            }

            # Retract any conflicting conclusions
            retracted = []
            for key in selected.retracts:
                if working_memory.get(key):
                    working_memory[key] = False
                    retracted.append(key)

            # Assert new conclusion and record trace
            fired_names.add(selected.name)
            fired_rules.append(selected)
            working_memory[selected.conclusion] = True

            trace.append(Trace(
                rule_name=selected.name,
                explanation=selected.explanation,
                evidence=evidence,
                conclusion=selected.conclusion,
                retracted=retracted,
                iteration=i,
            ))

        return fired_rules, working_memory, trace
