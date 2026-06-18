# Symbolic Molecular Classifier 

This is a symbolic classifier that takes SMILES strings representing organic chemicals as an input and classifies them by functional groups. I plan to extend this and use it in conjunction with a neural network to make this a fully Neuro-Symbolic classification system in the near future.

## How it works
1. Facts are extracted from a SMILES string using [RDKit](https://github.com/rdkit). Some examples include `has_COOH` and `has_aromatic_ring`.
2. Rules are loaded from the `rules.yaml` on startup.
3. The inference engine then loops over all of the rules in priority order. Each iteration it finds all rules with satisfied conditions, fires the highest priority rule, and repeats until no rules remain.
4. During this process if specified some rules can retract previous conclusions as more is learned about them. For example, once an alcohol conclusion is asserted, a subsequent phenol rule can fire and retract alcohol if the OH is actually on an aromatic carbon.
5. Every fired rule is then recorded into the trace.
6. Lastly everything is printed to show final conclusions and reasoning on that final conclusion.

## Installation
For this project I used Python 3.10.11, though it may work on other versions as well.
```bash
pip install -r requirements.txt
```

## Running
```bash
python .\main.py <SMILES arg>
```

or 

```bash
python .\main.py

Enter a single SMILES string: <SMILES arg>
```

or

In another project
```python
from mol_classifier import classify
result = classify("CC(=O)O")  # Acetic Acid
print(result["primary"])      # carboxylic_acid
print(result["conclusions"])  # ['carboxylic_acid', 'polar_molecule', 'carbonyl_compound']
```

## Extending Rules and Facts
To add rules you can simply follow the guide at the top of the `rules.yaml`. Many fields are optional, so there is no need to add them if they are empty in my example just note they can be added if needed.

How to write a  Rule:
```yaml
- name: carboxylic_acid_rule          # Unique identifier for the rule
  conclusion: carboxylic_acid         # The conclusion this rule asserts when it fires
  priority: 100                       # Higher = fires earlier when multiple rules match
  explanation: "Carboxyl group (-COOH) detected -> carboxylic acid"
  when:                               # Logical conditions that must be satisfied
    requires: [has_COOH]              # All of these facts must be True
    forbids: []                       # None of these may be True
    requires_any: []                  # At least one must be True
    requires_two_or_more: []          # At least two must be True
  retracts: []                        # Conclusions to remove if this rule fires
  enabled: True                       # Fully optional just to easily enable/disable rules
```

To add facts you can add them to `extract_facts()` in `mol_classifier.py`. Right now they are essentially SMARTS detectors using RDKit.


## Examples

**Ethanol (CCO):**
```bash
python .\main.py
Enter a single SMILES string: CCO

------------------------------------------------------------
Molecule   : CCO
Primary    : alcohol
Conclusions: alcohol, polar_molecule
------------------------------------------------------------
Reasoning trace:

Iteration 1 - alcohol
Explanation: Hydroxyl (-OH) on carbon detected
Raw facts: has_OH, has_sp3_C, has_hbond_donor, has_hbond_acceptor
Asserted: alcohol
------------------------------------------------------------

Iteration 2 - polar_molecule [chained]
Explanation: Polar functional group present -> polar molecule
Raw facts: has_OH, has_sp3_C, has_hbond_donor, has_hbond_acceptor
From rules: alcohol
Asserted: polar_molecule
------------------------------------------------------------
```

**Benzene (C1=CC=CC=C1):**
```bash
python .\main.py C1=CC=CC=C1

------------------------------------------------------------
Molecule   : C1=CC=CC=C1
Primary    : aromatic
Conclusions: aromatic
------------------------------------------------------------
Reasoning trace:

Iteration 1 - aromatic
Explanation: Six-membered aromatic ring (benzene-like) detected
Raw facts: has_aromatic_ring, has_ring
Asserted: aromatic
------------------------------------------------------------
```
