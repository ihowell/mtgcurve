import concurrent.futures
from dataclasses import dataclass
import itertools
import copy
import tqdm

from terminaltables import AsciiTable
import numpy as np

from azusa.mana_producers import PRODUCERS
from azusa.util import defaultdict, combinations_with_quantity


@dataclass
class State:
    num_cards_in_library: int
    turn_number: int

    # In play effects
    num_lands_in_play: int
    # activatable_permanents: list = []
    lands_per_turn: int
    extra_mana_per_turn: int

    # Cards in hand
    num_lands_in_hand: int
    mana_producers_in_hand: dict
    num_other_cards_in_hand: int

    # Cards in library
    num_lands_in_library: int
    mana_producers_in_library: dict
    num_other_cards_in_library: int

    def copy(self):
        new = copy.copy(self)
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

    return possibilities


def play_turn(state):
    remaining_mana = int(state.num_lands_in_play)
    assert remaining_mana >= 0
    remaining_mana += state.extra_mana_per_turn

    # for mana_producer in state.mana_producers_in_play:
    #     assert mana_producer.payoff >= mana_producer.input_cost
    #     remaining_mana += mana_producer.payoff - mana_producer.input_cost

    updates = defaultdict(lambda key: copy.copy(getattr(state, key)))

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

    if producer_played:
        state.mana_producers_in_hand = {
            p: q
            for p, q in state.mana_producers_in_hand.items() if q > 0
        }

    # state = state._replace(**updates)

    return state, mana_on_turn


def calculate_cmc_probs(num_cards_in_library,
                        mana_producers,
                        num_lands,
                        max_turns=3,
                        max_mana=5,
                        num_threads=4):
    num_opening_hands = 0
    for num_lands_in_hand in range(min(num_lands, 7) + 1):
        for num_producers_in_hand in range(
                min(len(mana_producers), 7 - num_lands_in_hand) + 1):
            num_opening_hands += choose(len(mana_producers),
                                        num_producers_in_hand)
    num_opening_hands = int(num_opening_hands)
    print('Num opening hands', num_opening_hands)

    def starting_hand_generator():
        log_hand_combinations = log_choose(num_cards_in_library, 7)
        mana_producer_list = itertools.chain(
            [[producer_id] * quantity
             for producer_id, quantity in mana_producers.items()])
        for num_lands_in_hand in range(min(num_lands, 7) + 1):
            log_land_comb = log_choose(num_lands, num_lands_in_hand)

            for num_producers_in_hand in range(
                    min(len(mana_producers) + 1, 7 - num_lands_in_hand) + 1):
                log_other_comb = log_choose(
                    num_cards_in_library - num_lands - len(mana_producers),
                    7 - num_lands_in_hand - num_producers_in_hand)
                log_prob = log_land_comb + log_other_comb - log_hand_combinations
                prob = np.exp(log_prob)

                # for producers in itertools.combinations(
                #         mana_producers, num_producers_in_hand):

                for producers in combinations_with_quantity(
                        mana_producers, num_producers_in_hand):

                    yield (num_lands_in_hand, producers,
                           7 - num_lands_in_hand - num_producers_in_hand, prob)

    def thread_calc_prob_table(hand_state, hand_prob):
        sub_prob_table = np.zeros((max_turns + 1, max_mana + 1),
                                  dtype=np.double)

        def calculate_subtree_probs(state, initial_prob):
            state, mana = play_turn(state)
            sub_prob_table[state.turn_number,
                           min(mana, max_mana)] += initial_prob
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
    num_other_cards_in_library = num_cards_in_library - len(
        mana_producers) - num_lands

    with concurrent.futures.ThreadPoolExecutor(
            max_workers=num_threads) as executor:
        threads = []
        for num_lands_in_hand, mana_producers_in_hand, num_other_cards_in_hand, initial_prob in starting_hand_generator(
        ):
            mana_producers_in_library = copy.copy(mana_producers)
            for item, quantity in mana_producers_in_hand.items():
                mana_producers_in_library[item] -= quantity
            mana_producers_in_library = dict(
                filter(lambda x: x[1] > 0, mana_producers_in_library.items()))

            state = State(
                num_cards_in_library=num_cards_in_library - num_lands_in_hand -
                len(mana_producers_in_hand) - num_other_cards_in_hand,
                turn_number=0,
                num_lands_in_play=0,
                lands_per_turn=1,
                extra_mana_per_turn=0,
                num_lands_in_hand=num_lands_in_hand,
                num_lands_in_library=num_lands - num_lands_in_hand,
                # inactive_mana_producers_in_play=[],
                # mana_producers_in_play=[],
                mana_producers_in_hand=mana_producers_in_hand,
                mana_producers_in_library=mana_producers_in_library,
                num_other_cards_in_hand=num_other_cards_in_hand,
                num_other_cards_in_library=num_other_cards_in_library -
                num_other_cards_in_hand)
            th = executor.submit(thread_calc_prob_table, state, initial_prob)
            threads.append(th)

        for th in tqdm.tqdm(threads, total=len(threads)):
            sub_prob_table = th.result()
            prob_table += sub_prob_table

    return prob_table


def display_prob_table(prob_table):
    max_turns = prob_table.shape[0] - 1
    max_mana = prob_table.shape[1] - 1
    table_data = [[''] + [f'Mana {i}'
                          for i in range(max_mana)] + [f'Mana {max_mana}+']]
    for turn in range(1, max_turns + 1):
        row = [f'Turn {turn}']
        for mana in range(max_mana + 1):
            row.append(f'{prob_table[turn][mana]*100:.2f}%')
        table_data.append(row)

    table = AsciiTable(table_data)
    print(table.table)
