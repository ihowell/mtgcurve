from collections import namedtuple

Card = namedtuple('Card', [
    'name',
    'cmc',
    'input_cost',
    'payoff',
])

PRODUCERS = {
    'Mana Crypt': Card('Mana Crypt', 0, 0, 2),
    'Sol Ring': Card('Sol Ring', 1, 0, 2),
    'Arcane Signet': Card('Arcane Signet', 2, 0, 1),
    'Mind Stone': Card('Mind Stone', 2, 0, 1),
    'Orzhov Signet': Card('Orzhov Signet', 2, 1, 2),
    'Golgari Signet': Card('Golgari Signet', 2, 1, 2),
    'Selesnya Signet': Card('Selesnya Signet', 2, 1, 2),
}
