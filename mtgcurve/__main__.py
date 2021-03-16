import fire

from .curve_probabilities import calculate_cmc_probs, display_prob_table
from .parse import parse_moxfield_url


def main(moxfield_url, max_turns=None, max_mana=7):
    cards_in_library, mana_producers, num_lands_in_library = parse_moxfield_url(moxfield_url)

    prob_table = calculate_cmc_probs(cards_in_library,
                                     mana_producers,
                                     num_lands_in_library,
                                     max_turns=max_turns,
                                     max_mana=max_mana)
    display_prob_table(prob_table)


if __name__ == '__main__':
    fire.Fire(main)
