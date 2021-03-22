import logging

import fire
import numpy as np

from azusa.curve_probabilities import calculate_cmc_probs, display_prob_table
from azusa.parse import parse_moxfield_url
from azusa.util import cumulative_probs


def main(moxfield_url,
         max_turns=None,
         max_mana=None,
         num_threads=4,
         debug=False):
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    cards_in_library, mana_producers, num_lands_in_library, max_cmc = parse_moxfield_url(
        moxfield_url)

    if max_turns is None:
        max_turns = max_cmc

    prob_table = calculate_cmc_probs(cards_in_library,
                                     mana_producers,
                                     num_lands_in_library,
                                     max_turns=max_turns,
                                     max_mana=max_mana or max_cmc,
                                     num_threads=num_threads)
    print('Probability of having X mana on turn Y')
    display_prob_table(prob_table)

    print('Probability of having at least X mana on turn Y')
    display_prob_table(cumulative_probs(prob_table))


if __name__ == '__main__':
    fire.Fire(main)
