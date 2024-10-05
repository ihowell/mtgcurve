import numpy as np
import terminaltables


def choose(a, b):
    return np.math.factorial(a) / np.math.factorial(b) / np.math.factorial(a -
                                                                           b)


def prob_discard_cards(starting_num_cards_in_hand):
    probs = []
    for num_discarded in range(4):
        if starting_num_cards_in_hand < 3 - num_discarded:
            prob = 0
        else:
            prob = \
                choose(3, num_discarded) * \
                choose(starting_num_cards_in_hand, 3 - num_discarded) / \
                choose(starting_num_cards_in_hand + 3, 3)
        probs.append(prob)
    return probs


if __name__ == '__main__':
    max_hand_size = 7
    hand_probs = []
    for hand_size in range(max_hand_size + 1):
        hand_probs.append(prob_discard_cards(hand_size))

    table_data = [['Hand Size', *list(range(max_hand_size + 1))]]
    hand_probs = np.transpose(hand_probs)
    for i, row in enumerate(hand_probs):
        table_row = [f'Discard {i}', *[f'{d:.3f}' for d in row]]
        table_data.append(table_row)

    table = terminaltables.AsciiTable(table_data)
    print(table.table)
