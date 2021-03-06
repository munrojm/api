from pymatgen import Composition, DummySpecie
from typing import Dict


def formula_to_criteria(formula: str) -> Dict:
    """
    Santizes formula into a dictionary to search with wild cards

    Arguments:
        formula: a chemical formula with wildcards in it for unknown elements

    Returns:
        Mongo style search criteria for this formula
    """
    dummies = "ADEGJLMQRXZ"

    if "*" in formula:
        # Wild card in formula
        nstars = formula.count("*")

        formula_dummies = formula.replace("*", "{}").format(*dummies[:nstars])

        comp = Composition(formula_dummies).reduced_composition
        crit = dict()
        crit["formula_anonymous"] = comp.anonymized_formula
        real_elts = [
            str(e)
            for e in comp.elements
            if not e.as_dict().get("element", "A") in dummies
        ]

        # Paranoia below about floating-point "equality"
        for el, n in comp.to_reduced_dict.items():
            if el in real_elts:
                crit["composition_reduced.{}".format(el)] = {
                    "$gt": 0.99 * n,
                    "$lt": 1.01 * n,
                }

        return crit
    elif any(isinstance(el, DummySpecie) for el in Composition(formula)):
        # Assume fully anonymized formula
        return {"formula_anonymous": Composition(formula).anonymized_formula}

    else:
        return {"formula_pretty": formula}
