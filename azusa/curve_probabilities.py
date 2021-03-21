import concurrent.futures
from dataclasses import dataclass, field
import itertools
import multiprocessing
import logging
import copy
import tqdm

from terminaltables import AsciiTable
import numpy as np

from azusa.mana_producers import PRODUCERS, ManaPermanent
from azusa.util import defaultdict, combinations_with_quantity


@dataclass
class State:
    num_cards_in_library: int
    turn_number: int

    # In play effects
    num_lands_in_play: int = 0
    activatable_permanents: dict = field(default_factory=dict)
    lands_per_turn: int = 1
    extra_mana_per_turn: int = 0

    # Cards in hand
    num_lands_in_hand: int = 0
    mana_producers_in_hand: dict = field(default_factory=dict)
    num_other_cards_in_hand: int = 0

    # Cards in library
    num_lands_in_library: int = 0
    mana_producers_in_library: dict = field(default_factory=dict)
    num_other_cards_in_library: int = 0

    def copy(self):
        new = copy.copy(self)
        new.activatable_permanents = copy.copy(new.activatable_permanents)
        new.mana_producers_in_hand = copy.copy(new.mana_producers_in_hand)
        new.mana_producers_in_library = copy.copy(
            new.mana_producers_in_library)
        return new


def log_choose(a, b):
    return np.log(np.math.factorial(a) + 0.0) - \
        np.log(np.math.factorial(b) + 0.0) - \
        np.log(np.math.factorial(a - b) + 0.0)


def choose(a, b):
    return (np.math.factorial(a) /
            np.math.factorial(b)) / np.math.factorial(a - b)


def start_turn(state):
    assert state.num_cards_in_library == state.num_lands_in_library + state.num_other_cards_in_library + sum(
        state.mana_producers_in_library.values()), state

    state.turn_number += 1

    possibilities = []

    # Draw a land
    prob = state.num_lands_in_library / state.num_cards_in_library
    new_state = state.copy()
    new_state.num_cards_in_library = state.num_cards_in_library - 1
    new_state.num_lands_in_library = state.num_lands_in_library - 1
    new_state.num_lands_in_hand = state.num_lands_in_hand + 1
    # mana_producers_in_hand=copy.copy(state.mana_producers_in_hand))
    possibilities.append((new_state, prob))

    # Draw a mana producer
    for producer_id, quantity in state.mana_producers_in_library.items():
        new_state = state.copy()

        prob = quantity / state.num_cards_in_library

        new_state.num_cards_in_library -= 1
        new_state.mana_producers_in_library[producer_id] -= 1
        if new_state.mana_producers_in_library[producer_id] == 0:
            del new_state.mana_producers_in_library[producer_id]

        if producer_id not in new_state.mana_producers_in_hand:
            new_state.mana_producers_in_hand[producer_id] = 0
        new_state.mana_producers_in_hand[producer_id] += 1

        possibilities.append((new_state, prob))

    # Draw any other card
    prob = state.num_other_cards_in_library / state.num_cards_in_library
    new_state = state.copy()
    new_state.num_cards_in_library = state.num_cards_in_library - 1
    new_state.num_other_cards_in_hand = state.num_other_cards_in_hand + 1
    new_state.num_other_cards_in_library = state.num_other_cards_in_library - 1
    possibilities.append((new_state, prob))

    sum_prob = sum(map(lambda x: x[1], possibilities), 0.)
    assert np.isclose(sum_prob, 1.), f'{sum_prob} != 1., {state}'

    return possibilities


def play_turn(state):
    remaining_mana = int(state.num_lands_in_play)
    assert remaining_mana >= 0
    remaining_mana += state.extra_mana_per_turn

    if state.num_lands_in_hand > 0:
        num_lands = min(state.num_lands_in_hand, state.lands_per_turn)
        state.num_lands_in_hand -= num_lands
        state.num_lands_in_play += num_lands
        remaining_mana += num_lands

    added_fast_producer = True
    while added_fast_producer:
        added_fast_producer = False
        for producer_id, quantity in state.mana_producers_in_hand.items():
            producer = PRODUCERS[producer_id]
            if producer.fast and producer.cmc <= remaining_mana and quantity > 0:
                added_fast_producer = True
                remaining_mana = producer.cast(state, remaining_mana)
                state.mana_producers_in_hand[producer_id] -= 1

    mana_on_turn = remaining_mana

    producer_played = False
    for producer_id, quantity in state.mana_producers_in_hand.items():
        producer = PRODUCERS[producer_id]
        if producer.cmc <= remaining_mana and quantity > 0:
            producer_played = True
            remaining_mana = producer.cast(state, remaining_mana)
            state.mana_producers_in_hand[producer_id] -= 1

    activated_ability = False
    for producer_id, quantity in state.activatable_permanents.items():
        producer = PRODUCERS[producer_id]
        if producer.activation_cost <= remaining_mana:
            remaining_mana = producer.activate(state, remaining_mana)
            activated_ability = True

    if producer_played:
        state.mana_producers_in_hand = dict(
            filter(lambda x: x[1] > 0, state.mana_producers_in_hand.items()))

    if activated_ability:
        state.activatable_permanents = dict(
            filter(lambda x: x[1] > 0, state.activatable_permanents.items()))

    return state, mana_on_turn


def calculate_subtree_probs(state, initial_prob, sub_prob_table, max_turns,
                            max_mana):
    state, mana = play_turn(state)
    sub_prob_table[state.turn_number, min(mana, max_mana)] += initial_prob
    assert state.turn_number >= 1, state
    assert mana >= 0, state
    if state.turn_number >= max_turns:
        return

    possible_states = start_turn(state)
    for child_state, prob in possible_states:
        calculate_subtree_probs(child_state, initial_prob * prob,
                                sub_prob_table, max_turns, max_mana)


def thread_calc_prob_table(args):
    hand_state, hand_prob, max_turns, max_mana = args
    sub_prob_table = np.zeros((max_turns + 1, max_mana + 1), dtype=np.double)
    child_prob = 0.
    for child_state, prob in start_turn(hand_state):
        child_prob += prob
        calculate_subtree_probs(child_state, hand_prob * prob, sub_prob_table,
                                max_turns, max_mana)

    return sub_prob_table


def calculate_cmc_probs(num_cards_in_library,
                        mana_producers,
                        num_lands,
                        max_turns=3,
                        max_mana=5,
                        num_threads=None):
    num_opening_hands = 0
    for num_lands_in_hand in range(min(num_lands, 7) + 1):
        for num_producers_in_hand in range(
                min(len(mana_producers), 7 - num_lands_in_hand) + 1):
            num_opening_hands += choose(len(mana_producers),
                                        num_producers_in_hand)
    num_opening_hands = int(num_opening_hands)
    print('Num opening hands', num_opening_hands)

    def starting_hand_generator():
        total_prob = 0
        log_hand_combinations = log_choose(num_cards_in_library, 7)
        for num_lands_in_hand in range(min(num_lands, 7) + 1):
            log_land_comb = log_choose(num_lands, num_lands_in_hand)

            for num_producers_in_hand in range(
                    min(len(mana_producers), 7 - num_lands_in_hand) + 1):

                num_other_cards_in_hand = 7 - num_lands_in_hand - num_producers_in_hand

                log_other_comb = log_choose(
                    num_cards_in_library - num_lands - len(mana_producers),
                    num_other_cards_in_hand)
                log_prob = log_land_comb + log_other_comb - log_hand_combinations
                initial_prob = np.exp(log_prob)

                logging.debug(
                    f'Num lands={num_lands_in_hand}, prod={num_producers_in_hand}, other={num_other_cards_in_hand}'
                )
                logging.debug(
                    f'Log probs lands={log_land_comb:.5f}, other={log_other_comb:.5f}, total={log_hand_combinations:.5f}'
                )

                for mana_producers_in_hand in combinations_with_quantity(
                        mana_producers, num_producers_in_hand):

                    mana_producers_in_library = copy.copy(mana_producers)
                    for item, quantity in mana_producers_in_hand.items():
                        mana_producers_in_library[item] -= quantity
                    mana_producers_in_library = dict(
                        filter(lambda x: x[1] > 0,
                               mana_producers_in_library.items()))

                    state = State(
                        num_cards_in_library=num_cards_in_library -
                        num_lands_in_hand - len(mana_producers_in_hand) -
                        num_other_cards_in_hand,
                        turn_number=0,
                        num_lands_in_hand=num_lands_in_hand,
                        num_lands_in_library=num_lands - num_lands_in_hand,
                        mana_producers_in_hand=mana_producers_in_hand,
                        mana_producers_in_library=mana_producers_in_library,
                        num_other_cards_in_hand=num_other_cards_in_hand,
                        num_other_cards_in_library=num_other_cards_in_library -
                        num_other_cards_in_hand)
                    yield (state, initial_prob, max_turns, max_mana)
                    total_prob += initial_prob
        logging.debug(f'Total probability from starting hand {total_prob}')

    prob_table = np.zeros((max_turns + 1, max_mana + 1), dtype=np.double)
    num_other_cards_in_library = num_cards_in_library - len(
        mana_producers) - num_lands

    with multiprocessing.Pool(processes=num_threads) as pool:
        sub_prob_tables = pool.imap_unordered(thread_calc_prob_table,
                                              starting_hand_generator())

        for sub_prob_table in tqdm.tqdm(sub_prob_tables,
                                        total=num_opening_hands):

            prob_table += sub_prob_table

    return prob_table


def display_prob_table(prob_table, print_total_row_prob=False):
    max_turns = prob_table.shape[0] - 1
    max_mana = prob_table.shape[1] - 1
    table_data = [[''] + [f'Mana {i}'
                          for i in range(max_mana)] + [f'Mana {max_mana}+']]
    for turn in range(1, max_turns + 1):
        row = [f'Turn {turn}']
        row_prob = 0
        for mana in range(max_mana + 1):
            row.append(f'{prob_table[turn][mana]*100:.2f}%')
            row_prob += prob_table[turn][mana]
        if print_total_row_prob:
            row.append(f'{row_prob*100:.2f}%')

        table_data.append(row)

    table = AsciiTable(table_data)
    print(table.table)
