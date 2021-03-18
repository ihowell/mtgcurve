from azusa.mana_producers import Card
from azusa.curve_probabilities import calculate_cmc_probs, display_prob_table

def test_artifact_probs():
    num_lands = 4
    num_other = 7
    mana_producers = [
        Card(name='Mana Crypt', cmc=0, input_cost=0, payoff=2, turns_til_active=0),
        Card(name='Sol Ring', cmc=1, input_cost=0, payoff=2, turns_til_active=0),
    ]

    probs = calculate_cmc_probs(len(mana_producers) + num_lands + num_other, mana_producers, num_lands, max_turns=2)

    display_prob_table(probs)
