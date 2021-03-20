import constraint


class defaultdict(dict):
    def __init__(self, factory):
        self.factory = factory

    def __missing__(self, key):
        self[key] = self.factory(key)
        return self[key]


def combinations_with_quantity(items_dict, total):
    problem = constraint.Problem()
    global_scope = []
    for item_id, quantity in items_dict.items():
        problem.addVariable(item_id, list(range(quantity + 1)))
        global_scope.append(item_id)
    problem.addConstraint(constraint.ExactSumConstraint(total), global_scope)

    for solution in problem.getSolutionIter():
        solution = dict(filter(lambda x: x[1] > 0, solution.items()))
        yield solution
