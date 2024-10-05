import numpy as np
import terminaltables


def log_choose(a, b):
    return np.log(np.math.factorial(a) + 0.0) - \
        np.log(np.math.factorial(b) + 0.0) - \
        np.log(np.math.factorial(a - b) + 0.0)


def prob_apostles(total_cards_in_library, total_apostles_in_library):
    cached_probs = {}

    def prob_apostles_recur(cards_in_library, apostles_in_library,
                            triggers_on_stack):
        if triggers_on_stack == 0:
            probs = np.zeros((total_apostles_in_library + 1, ))
            probs[apostles_in_library] = 1.
            return probs

        if cards_in_library - total_apostles_in_library <= 3:
            probs = np.zeros((total_apostles_in_library + 1, ))
            probs[0] = 1.
            return probs

        key = f'{cards_in_library}_{apostles_in_library}_{triggers_on_stack}'
        if key in cached_probs:
            return cached_probs[key]

        triggers_on_stack -= 1

        other_in_library = cards_in_library - apostles_in_library

        sum_prob = 0.
        probs = []
        for apostles_hit in range(min(apostles_in_library + 1, 5)):
            if 4 - apostles_hit > other_in_library:
                continue
            log_prior_prob = \
                log_choose(apostles_in_library, apostles_hit) + \
                log_choose(other_in_library, 4 - apostles_hit) - \
                log_choose(cards_in_library, 4)

            sub_prob = prob_apostles_recur(cards_in_library - 4,
                                           apostles_in_library - apostles_hit,
                                           triggers_on_stack + apostles_hit)
            prob = np.exp(log_prior_prob) * sub_prob
            sum_prob += np.exp(log_prior_prob)
            probs.append(prob)
        assert len(probs) > 0
        probs = np.array(probs)
        assert len(probs.shape) == 2, f'probs {probs}'
        assert np.isclose(
            np.sum(sum_prob),
            1.), f'{key} {other_in_library} {probs} {np.sum(sum_prob)}'
        probs = np.sum(probs, axis=0)
        cached_probs[key] = probs
        return probs

    return prob_apostles_recur(total_cards_in_library,
                               total_apostles_in_library, 1)


def main():
    num_cards_in_library = 80
    num_apostles_in_library = 33

    probs = prob_apostles(num_cards_in_library, num_apostles_in_library)

    table_data = [
        ['Apostles in Library', 'Probability'],
        *[[i, f'{p:.3f}'] for i, p in enumerate(probs)],
    ]

    table = terminaltables.AsciiTable(table_data)
    print(table.table)


if __name__ == '__main__':
    main()
