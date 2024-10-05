from dataclasses import dataclass, field, asdict
import inspect
import logging

import fire
import numpy as np

from azusa.curve_probabilities import calculate_cmc_probs, display_prob_table
from azusa.parse import parse_moxfield_url
from azusa.util import cumulative_probs


@dataclass
class Settings:
    max_turns: int = None
    max_mana: int = None
    num_threads: int = None
    debug: bool = False

    top_of_library_revealed: bool = False
    colored_mana_calculation: bool = False

    enable_mana_permanent: bool = True
    enable_land_fetcher: bool = True
    enable_extra_land: bool = True
    enable_sacrifice_permanent: bool = True


def main(moxfield_url,
         max_turns: int = None,
         max_mana: int = None,
         num_threads: int = None,
         debug: bool = False,
         top_of_library_revealed: bool = False,
         colored_mana_calculation: bool = False,
         enable_mana_permanent: bool = True,
         enable_land_fetcher: bool = True,
         enable_extra_land: bool = True,
         enable_sacrifice_permanent: bool = True):

    settings_params = list(
        inspect.signature(Settings.__init__).parameters.keys())
    settings_kwargs = {
        k: v
        for k, v in locals().items() if k in settings_params
    }
    settings = Settings(**settings_kwargs)
    print(settings)
    # print('settings', kwargs)
    return
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


def build_settings(max_turns: int = None,
                   max_mana: int = None,
                   num_threads: int = None,
                   debug: bool = False,
                   top_of_library_revealed: bool = False,
                   colored_mana_calculation: bool = False,
                   enable_mana_permanent: bool = True,
                   enable_land_fetcher: bool = True,
                   enable_extra_land: bool = True,
                   enable_sacrifice_permanent: bool = True):
    return Settings(max_turns, max_mana, num_threads, debug,
                    top_of_library_revealed, colored_mana_calculation,
                    enable_mana_permanent, enable_land_fetcher,
                    enable_extra_land, enable_sacrifice_permanent)


if __name__ == '__main__':
    fire.Fire(main)
    # settings = Settings()
    # settings = fire.Fire(build_settings)
    # print('args', settings)
