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
    for card, card_data in mainboard.items():
        if card in PRODUCERS:
            mana_producers.append(PRODUCERS[card])
        elif 'Land' in card_data['card']['type_line']:
            num_lands += card_data['quantity']

    print('num in library', len(mainboard))
    print('num lands:', num_lands)
    print('mana producers:')
    for producer in mana_producers:
        print('\t', producer.name)

    return len(mainboard), mana_producers, num_lands


if __name__ == '__main__':
    fire.Fire(parse_moxfield_url)
