from azusa.curve_probabilities import calculate_cmc_probs, display_prob_table


def test_artifact_probs():
    num_lands = 4
    num_other = 7
    mana_producers = {'Mana Crypt': 1, 'Sol Ring': 1}

    probs = calculate_cmc_probs(len(mana_producers) + num_lands + num_other,
                                mana_producers,
                                num_lands,
                                max_turns=2)

    display_prob_table(probs)
