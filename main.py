import sys
from mol_classifier import classify


def print_trace(result: dict) -> None:
    print("\n" + "-" * 60)
    print(f"Molecule   : {result.get('molecule')}")
    print(f"Primary    : {result.get('primary')}")
    conclusions = result.get('conclusions') or []
    print(f"Conclusions: {', '.join(conclusions) if conclusions else '[]'}")
    print("-" * 60)
    print("Reasoning trace:")

    for entry in result.get("trace", []):
        iteration = entry.iteration
        rule_name = entry.rule_name
        explanation = entry.explanation
        evidence = entry.evidence or {}
        facts = evidence.get("facts") or []
        from_rules = evidence.get("conclusions") or []
        conclusion = entry.conclusion

        retracted = entry.retracted or []
        chained = bool(from_rules)
        tag = " [chained]" if chained else ""

        print(f"\nIteration {iteration} - {rule_name}{tag}")
        if explanation:
            print(f"Explanation: {explanation}")
        if facts:
            print(f"Raw facts: {', '.join(facts)}")
        if from_rules:
            print(f"From rules: {', '.join(from_rules)}")
        if retracted:
            print(f"Retracted: {', '.join(retracted)}")
        print(f"Asserted: {conclusion}")
        print("-" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        smiles = sys.argv[1].strip()
    else:
        smiles = input("Enter a single SMILES string: ").strip()

    try:
        result = classify(smiles)
    except Exception as exc:
        print(f"Error classifying '{smiles}': {exc}")
        sys.exit(1)

    print_trace(result)
