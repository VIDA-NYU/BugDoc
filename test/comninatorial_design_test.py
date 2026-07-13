import copy
import itertools

from bugdoc.utils.combinatorial_design import generate_tuples


def _all_pairs_covered(rows, parameters):
    keys = list(parameters)
    for pair in itertools.combinations(keys, 2):
        values0 = parameters[pair[0]]
        values1 = parameters[pair[1]]
        covered = {
            (row[pair[0]], row[pair[1]])
            for row in rows
            if row[pair[0]] in values0 and row[pair[1]] in values1
        }
        if len(covered) != len(values0) * len(values1):
            return False
    return True


def test_generate_tuples_is_deterministic_and_pairwise_covers():
    parameters = {
        "A": ["a0", "a1"],
        "B": ["b0", "b1"],
        "C": ["c0", "c1", "c2"],
    }

    rows1 = generate_tuples(copy.deepcopy(parameters))
    rows2 = generate_tuples(copy.deepcopy(parameters))

    assert rows1 == rows2
    assert _all_pairs_covered(rows1, parameters)
