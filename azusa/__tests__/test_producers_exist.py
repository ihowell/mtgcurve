import pytest

import scrython

from azusa.mana_producers import PRODUCERS


@pytest.mark.slow_integration_test
def test_each_mana_producer_exists():
    for name, card in PRODUCERS.items():
        assert name == card.name

    for name, card in PRODUCERS.items():
        card = scrython.cards.Named(exact=name)
        assert card.name() == name
