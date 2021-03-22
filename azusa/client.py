import asyncio
import streamlit as st
import numpy as np
import scrython
import time
import pandas as pd
import os

from azusa.curve_probabilities import calculate_cmc_probs
from azusa.parse import parse_moxfield_url
from azusa.util import cumulative_probs


def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()


class ProgressBar:
    def __init__(self, iterable, total):
        self.progress = 0
        self.total = total
        self.progress_bar = st.progress(0)
        self.status_text = st.empty()
        self.iterable = iterable

    def update(self, increment=1):
        self.progress += increment
        self.progress_bar.progress(self.progress / self.total)

    def __iter__(self):
        self.progress = 0
        self.progress_bar.progress(0.)
        self.status_text.text(f'{self.progress} / {self.total}')

        for i in self.iterable:
            yield i
            self.progress += 1
            self.progress_bar.progress(self.progress / self.total)
            self.status_text.text(f'{self.progress} / {self.total}')


loop = get_or_create_eventloop()

if 'AZUSA_LOCAL' in os.environ:
    server_is_local = os.environ['AZUSA_LOCAL']
else:
    server_is_local = False

st.title('Azusa: Probability Curve Calculator')

max_turns = st.sidebar.slider('Max Turns', 1, 10, 3)
max_mana = st.sidebar.slider('Max Mana', 1, 20, 10)

if server_is_local:
    num_processes = st.sidebar.slider('Process Count', 1, os.cpu_count(),
                                      min(4, os.cpu_count()))
else:
    num_processes = 1
    st.sidebar.write('''
Process Count: 1, Download app at https://github.com/ihowell/azusa to use local resources.
    ''')

moxfield_url = st.text_input('Moxfield deck url:')
if moxfield_url:
    cards_in_library, mana_producers, num_lands_in_library, max_cmc = parse_moxfield_url(
        moxfield_url)

    st.text('Ramp Detected:')
    uris = []
    for producer_id in mana_producers:
        card = scrython.cards.Named(exact=producer_id)
        uris.append(card.image_uris()['png'])
    st.image(uris, width=120)

    if max_turns is None:
        max_turns = max_cmc

    prob_table = calculate_cmc_probs(cards_in_library,
                                     mana_producers,
                                     num_lands_in_library,
                                     max_turns=max_turns,
                                     max_mana=max_mana or max_cmc,
                                     num_threads=num_processes,
                                     progress_bar=ProgressBar)

    cumulative_table = cumulative_probs(prob_table)

    prob_data_frame = pd.DataFrame(prob_table,
                                   columns=(f'Mana {i}'
                                            for i in range(max_mana + 1)),
                                   index=(f'Turn {i}'
                                          for i in range(max_turns + 1)))
    st.write('Probability to have access to X mana on turn Y')
    st.dataframe(prob_data_frame.style.format('{:.2%}'))

    prob_data_frame = pd.DataFrame(cumulative_table,
                                   columns=(f'Mana {i}'
                                            for i in range(max_mana + 1)),
                                   index=(f'Turn {i}'
                                          for i in range(max_turns + 1)))
    st.write('Probability to have access to at least X mana on turn Y')
    st.dataframe(prob_data_frame.style.format('{:.2%}'))
