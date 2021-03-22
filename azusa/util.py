import constraint
import numpy as np


class defaultdict(dict):
    def __init__(self, factory):
        self.factory = factory

    def __missing__(self, key):
        self[key] = self.factory(key)
        return self[key]


def combinations_with_quantity(items_dict, total):
    assert len(
        items_dict
    ) > 0 or total == 0, f'len(items_dict)={len(items_dict)}, total={total}'
    if total == 0:
        yield {}
        return

    total_quantity = 0
    problem = constraint.Problem()
    global_scope = []
    for item_id, quantity in items_dict.items():
        problem.addVariable(item_id, list(range(quantity + 1)))
        global_scope.append(item_id)
        total_quantity += quantity
    assert total_quantity >= total

    problem.addConstraint(constraint.ExactSumConstraint(total), global_scope)

    for solution in problem.getSolutionIter():
        solution = dict(filter(lambda x: x[1] > 0, solution.items()))
        yield solution


def cumulative_probs(prob_table):
    rows = []
    for i in range(prob_table.shape[1]):
        rows.append(np.sum(prob_table[:, i:], axis=1))
    rows = np.stack(rows, axis=1)
    return rows
