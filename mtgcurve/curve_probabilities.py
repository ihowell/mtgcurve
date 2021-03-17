from collections import namedtuple
import itertools
import copy
import tqdm
import concurrent.futures
import asyncio

from terminaltables import AsciiTable
import numpy as np

from .mana_producers import PRODUCERS
from .util import defaultdict


State = namedtuple('State', [
    'num_cards_in_library',
    'turn_number',
    'num_lands_in_play',
    'num_lands_in_hand',
    'num_lands_in_library',
    'inactive_mana_producers_in_play',
    'mana_producers_in_play',
    'mana_producers_in_hand',
    'mana_producers_in_library',
    'num_other_cards_in_hand',
    'num_other_cards_in_library',
])


def log_choose(a, b):
    return np.log(np.math.factorial(a) + 0.0) - \
        np.log(np.math.factorial(b) + 0.0) - \
        np.log(np.math.factorial(a - b) + 0.0)


    def test():
        num_cards_in_library = 98
        num_lands = 33
        num_producers_in_library = 11
        num_other_in_library = num_cards_in_library - num_lands - num_producers_in_library
        log_hand_combinations = log_choose(num_cards_in_library, 7)
        for num_lands_in_hand in range(8):
            num_other_in_hand = 7 - num_lands_in_hand
            log_land_comb = log_choose(num_lands, num_lands_in_hand)
            log_prod_comb = np.log(np.math.factorial(0))
            log_other_comb = log_choose(num_other_in_library,
                                        num_other_in_hand)
            log_prob = log_land_comb + log_prod_comb + log_other_comb - log_hand_combinations
            prob = np.exp(log_prob)



def choose(a, b):
    return (np.math.factorial(a) / np.math.factorial(b)) / np.math.factorial(a - b)


def start_turn(state):
    turn_number = state.turn_number + 1
    inactive_mana_producers_in_play = []
    mana_producers_in_play = copy.copy(state.mana_producers_in_play)
    for mana_producer, turns_til_active in state.inactive_mana_producers_in_play:
        assert turns_til_active > 0
        if turns_til_active == 1:
            mana_producers_in_play.append(mana_producer)
        else:
            inactive_mana_producers_in_play.append((mana_producer, turns_til_active - 1))

    state = state._replace(inactive_mana_producers_in_play=inactive_mana_producers_in_play,
                           mana_producers_in_play=mana_producers_in_play)

    possibilities = []

    total_prob = 0.

    # Draw a land
    prob = state.num_lands_in_library / state.num_cards_in_library
    total_prob += prob
    # print('Draw land prob', prob)
    new_state = state._replace(
        turn_number=turn_number,
        num_cards_in_library=state.num_cards_in_library - 1,
        num_lands_in_library=state.num_lands_in_library - 1,
        num_lands_in_hand=state.num_lands_in_hand + 1,
        mana_producers_in_hand=copy.copy(state.mana_producers_in_hand))
    possibilities.append((new_state, prob))

    # Draw a mana producer
    for i, producer in enumerate(state.mana_producers_in_library):
        prob = 1. / state.num_cards_in_library
        total_prob += prob
        # print('Draw producer prob', prob)
        mana_producers_in_library = copy.copy(state.mana_producers_in_library)
        mana_producers_in_hand = copy.copy(state.mana_producers_in_hand)
        producer = mana_producers_in_library.pop(i)
        mana_producers_in_hand.append(producer)
        new_state = state._replace(
            num_cards_in_library=state.num_cards_in_library - 1,
            mana_producers_in_library=mana_producers_in_library,
            mana_producers_in_hand=mana_producers_in_hand,
            turn_number=turn_number)
        possibilities.append((new_state, prob))

    # Draw any other card
    prob = state.num_other_cards_in_library / state.num_cards_in_library
    total_prob += prob
    # print('Draw other prob', prob)
    new_state = state._replace(
        turn_number=turn_number,
        num_cards_in_library=state.num_cards_in_library - 1,
        num_other_cards_in_hand=state.num_other_cards_in_hand + 1,
        num_other_cards_in_library=state.num_other_cards_in_library - 1,
        mana_producers_in_hand=copy.copy(state.mana_producers_in_hand))
    possibilities.append((new_state, prob))
    # print('total prob', total_prob)

    return possibilities


def play_turn(state):
    remaining_mana = int(state.num_lands_in_play)
    assert remaining_mana >= 0

    for mana_producer in state.mana_producers_in_play:
        assert mana_producer.payoff >= mana_producer.input_cost
        remaining_mana += mana_producer.payoff - mana_producer.input_cost

    updates = defaultdict(lambda key: copy.copy(getattr(state, key)))

    if state.num_lands_in_hand > 0:
        updates['num_lands_in_hand'] -= 1
        updates['num_lands_in_play'] += 1
        remaining_mana += 1

    fast_producers = [m for m in state.mana_producers_in_hand if m.payoff > m.cmc + m.input_cost and m.turns_til_active == 0]
    added_fast_producer = True
    while added_fast_producer:
        added_fast_producer = False
        i = 0
        while i < len(fast_producers):
            mana_producer = fast_producers[i]
            if mana_producer.cmc + mana_producer.input_cost <= remaining_mana:
                j = updates['mana_producers_in_hand'].index(mana_producer)
                updates['mana_producers_in_hand'].pop(j)
                remaining_mana += mana_producer.payoff - mana_producer.cmc - mana_producer.input_cost
                fast_producers.pop(i)
                added_fast_producer = True
            else:
                i += 1

    mana_on_turn = remaining_mana

    producers_played = []
    for producer in state.mana_producers_in_hand:
        if producer.cmc <= remaining_mana:
            producers_played.append(producer)
            if producer.turns_til_active == 0:
                updates['mana_producers_in_play'].append(producer)
                remaining_mana -= producer.cmc
                if remaining_mana >= producer.input_cost:
                    remaining_mana += producer.payoff - producer.input_cost
            else:
                updates['inactive_mana_producers_in_play'].append((producer, producer.turns_til_active))
                remaining_mana -= producer.cmc

    if len(producers_played) > 0:
        updates['mana_producers_in_hand'] = [p for p in state.mana_producers_in_hand if p not in producers_played]

    state = state._replace(**updates)

    return state, mana_on_turn


def calculate_cmc_probs(num_cards_in_library, mana_producers, num_lands, max_turns=3, max_mana=5, num_threads=4):
    num_opening_hands = 0
    for num_lands_in_hand in range(min(num_lands, 7) + 1):
        for num_producers_in_hand in range(min(len(mana_producers), 7 - num_lands_in_hand) + 1):
            num_opening_hands += choose(len(mana_producers), num_producers_in_hand)
    num_opening_hands = int(num_opening_hands)
    print('Num opening hands', num_opening_hands)

    def starting_hand_generator():
        log_hand_combinations = log_choose(num_cards_in_library, 7)
        for num_lands_in_hand in range(min(num_lands, 7) + 1):
            log_land_comb = log_choose(num_lands, num_lands_in_hand)

            for num_producers_in_hand in range(min(len(mana_producers) + 1, 7 - num_lands_in_hand) + 1):
                log_other_comb = log_choose(num_cards_in_library - num_lands - len(mana_producers),
                                            7 - num_lands_in_hand - num_producers_in_hand)
                log_prob = log_land_comb + log_other_comb - log_hand_combinations
                prob = np.exp(log_prob)
                for producers in itertools.combinations(mana_producers, num_producers_in_hand):
                    yield (num_lands_in_hand, list(producers), 7 - num_lands_in_hand - num_producers_in_hand, prob)



    def thread_calc_prob_table(hand_state, hand_prob):
        sub_prob_table = np.zeros((max_turns + 1, max_mana + 1), dtype=np.double)

        def calculate_subtree_probs(state, initial_prob):
            state, mana = play_turn(state)
            sub_prob_table[state.turn_number, min(mana, max_mana)] += initial_prob
            assert state.turn_number >= 1, state
            assert mana >= 0, state
            if state.turn_number >= max_turns:
                return

            possible_states = start_turn(state)
            for child_state, prob in possible_states:
                calculate_subtree_probs(child_state, initial_prob * prob)

        child_prob = 0.
        for child_state, prob in start_turn(hand_state):
            child_prob += prob
            calculate_subtree_probs(child_state, hand_prob * prob)

        return sub_prob_table


    prob_table = np.zeros((max_turns + 1, max_mana + 1), dtype=np.double)
    num_other_cards_in_library = num_cards_in_library - len(mana_producers) - num_lands

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        threads = []
        for num_lands_in_hand, mana_producers_in_hand, num_other_cards_in_hand, initial_prob in starting_hand_generator():
            mana_producers_in_library = [m for m in mana_producers if m not in mana_producers_in_hand]
            state = State(num_cards_in_library=num_cards_in_library - num_lands_in_hand - len(mana_producers_in_hand) - num_other_cards_in_hand,
                          turn_number=0,
                          num_lands_in_play=0,
                          num_lands_in_hand=num_lands_in_hand,
                          num_lands_in_library=num_lands - num_lands_in_hand,
                          inactive_mana_producers_in_play=[],
                          mana_producers_in_play=[],
                          mana_producers_in_hand=mana_producers_in_hand,
                          mana_producers_in_library=mana_producers_in_library,
                          num_other_cards_in_hand=num_other_cards_in_hand,
                          num_other_cards_in_library=num_other_cards_in_library - num_other_cards_in_hand)
            th = executor.submit(thread_calc_prob_table, state, initial_prob)
            threads.append(th)

        for th in tqdm.tqdm(threads, total=len(threads)):
            sub_prob_table = th.result()
            prob_table += sub_prob_table

    return prob_table


def display_prob_table(prob_table):
    max_turns = prob_table.shape[0] - 1
    max_mana = prob_table.shape[1] - 1
    table_data = [[''] + [f'Mana {i}' for i in range(max_mana)] + [f'Mana {max_mana}+' ,'Total']]
    for turn in range(1, max_turns + 1):
        row = [f'Turn {turn}']
        for mana in range(max_mana + 1):
            row.append(f'{prob_table[turn][mana]*100:.2f}%')
        total = np.sum(prob_table[turn])
        row.append(f'{total*100:.2f}%')
        table_data.append(row)
    table = AsciiTable(table_data)
    print(table.table)


def main():
    mana_rock_names = [
        'Mana Crypt',
        'Sol Ring',
        'Arcane Signet',
        'Mind Stone',
        'Orzhov Signet',
        'Golgari Signet',
        'Selesnya Signet',
    ]

    mana_rocks = [PRODUCERS[name] for name in mana_rock_names]

    max_turns = 7
    max_mana = 7

    prob_table = calculate_cmc_probs(99, [], 36)
    display_prob_table(prob_table)


if __name__ == '__main__':
    main()
