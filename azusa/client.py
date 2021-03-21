import streamlit as st
import numpy as np

from azusa.curve_probabilities import calculate_cmc_probs
from azusa.parse import parse_moxfield_url

st.title('Azusa: Curve Probability Calculator')

moxfield_url = st.text_input('Moxfield deck url:')
if moxfield_url:
    st.text(moxfield_url)

    num_threads = None
    cards_in_library, mana_producers, num_lands_in_library, max_cmc = parse_moxfield_url(
        moxfield_url)

    max_turns = 6
    max_mana = 10

    if max_turns is None:
        max_turns = max_cmc

    prob_table = calculate_cmc_probs(cards_in_library,
                                     mana_producers,
                                     num_lands_in_library,
                                     max_turns=max_turns,
                                     max_mana=max_mana or max_cmc,
                                     num_threads=num_threads)

    st.write(prob_table * 100.)
