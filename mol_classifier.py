from inference_engine import InferenceEngine
from rules import RULES
from rdkit import Chem


ENGINE = InferenceEngine(RULES)


def match(molecule, pattern) -> bool:
    return molecule.HasSubstructMatch(Chem.MolFromSmarts(pattern))


def extract_facts(smiles_molecule) -> dict:

    molecule = Chem.MolFromSmiles(smiles_molecule)
    if molecule is None:
        raise ValueError(f"Invalid SMILES: {smiles_molecule}")

    return {
        # structural metadata
        "num_atoms":        molecule.GetNumAtoms(),
        "num_bonds":        molecule.GetNumBonds(),

        # chemical facts
        "has_COOH":         match(molecule, "[CX3](=O)[OX1H0-,OX2H1]"),
        "has_amide":        match(molecule, "[NX3][CX3](=O)"),
        "has_primary_or_secondary_amine": match(molecule, "[NX3;H2,H1;!$(NC=O)]"),
        "has_ester":        match(molecule, "[CX3](=O)[OX2][#6]"),
        "has_aldehyde":     match(molecule, "[CX3H1](=O)"),
        "has_acyl_halide":  match(molecule, "[CX3](=[OX1])[F,Cl,Br,I]"),
        "has_halogen":      match(molecule, "[#6][F,Cl,Br,I]"),
        "has_ketone":       match(molecule, "[#6][CX3](=O)[#6]"),
        "has_OH":           match(molecule, "[#6][OX2H]"),
        "has_NH2":          match(molecule, "[NX3H2][CX4]"),
        "has_anhydride":    match(molecule, "[CX3](=[OX1])[OX2][CX3](=[OX1])"),
        "has_thiol":        match(molecule, "[SX2H]"),
        "has_imine":        match(molecule, "[CX3;$([C]([#6])[#6]),$([CH][#6])]=[NX2][#6]"),
        "has_aromatic_ring": match(molecule, "c1ccccc1"),
        "has_ring":         molecule.GetRingInfo().NumRings() > 0,
        "has_sp3_C":        match(molecule, "[CX4H3,CX4H2,CX4H1]"),
        "has_carboxylate_ion": match(molecule, "[CX3](=O)[O-]"),
        "has_phenol":       match(molecule, "[OX2H][cX3]:[c]"),
        "has_enol":         match(molecule, "[OX2H][#6X3]=[#6]"),
        "has_ether":        match(molecule, "[OD2]([#6])[#6]"),
        "has_nitro":        match(molecule, "[$([NX3](=O)=O),$([NX3+](=O)[O-])][!#8]"),
        "has_nitrile":      match(molecule, "[NX1]#[CX2]"),
        "has_sulfone":      match(molecule, "[$([#16X4](=[OX1])=[OX1]),$([#16X4+2]([OX1-])[OX1-])]"),
        "has_sulfide":      match(molecule, "[#16X2H0][!#16]"),
        "has_disulfide":    match(molecule, "[#16X2H0][#16X2H0]"),
        "has_hbond_donor":  match(molecule, "[!H0;#7,#8,#9]"),
        "has_hbond_acceptor": match(molecule, "[!$([#6,F,Cl,Br,I,o,s,nX3,#7v5,#15v5,#16v4,#16v6,*+1,*+2,*+3])]"),
        "is_zwitterion":    match(molecule, "[+1]~*~*~[-1]"),
    }


def classify(smiles: str) -> dict:
    facts = extract_facts(smiles)
    fired, final_memory, trace = ENGINE.infer(facts)

    # No rules matched
    if not fired:
        return {
            "molecule": smiles,
            "primary": "unknown",
            "conclusions": [],
            "fired_rules": [],
            "explanations": ["No rules matched."],
            "facts": facts,
        }

    conclusions = list(dict.fromkeys(r.conclusion for r in fired))
    primary = max(fired, key=lambda r: r.priority)

    return {
        "molecule": smiles,
        "primary": primary.conclusion,
        "conclusions": conclusions,
        "trace": trace,
        "facts": facts,
    }
