import requests
import fire

from .mana_producers import PRODUCERS

def parse_moxfield_url(moxfield_url):
    deck_id = moxfield_url.split('/')[-1]
    url = f'https://api.moxfield.com/v2/decks/all/{deck_id}'
    print('Retrieving deck data from', url)
    resp = requests.get(url=url)
    data = resp.json()
    print('Finished getting deck data')

    mainboard = data['mainboard']


    mana_producers = []
    num_lands = 0
    max_cmc = 0
    for card, card_data in mainboard.items():
        if card in PRODUCERS:
            mana_producers.append(PRODUCERS[card])
        elif 'Land' in card_data['card']['type_line']:
            num_lands += card_data['quantity']
        max_cmc = max(max_cmc, card_data['card']['cmc'])

    max_cmc = int(max_cmc)

    print('Number of cards in library', len(mainboard))
    print('Number of lands:', num_lands)
    print('Maximum CMC in library:', max_cmc)
    print('Recognized mana producers:')
    for i, producer in enumerate(mana_producers):
        print('\t', i, producer.name)

    return len(mainboard), mana_producers, num_lands, max_cmc


if __name__ == '__main__':
    fire.Fire(parse_moxfield_url)
