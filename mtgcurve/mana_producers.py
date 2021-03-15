from collections import namedtuple

Card = namedtuple('Card', [
    'name',
    'cmc',
    'input_cost',
    'payoff',
])

PRODUCERS = {
    'mana crypt': Card('Mana Crypt', 0, 0, 2),
    'sol ring': Card('Sol Ring', 1, 0, 2),
    'arcane signet': Card('Arcane Signet', 2, 0, 1),
    'mind stone': Card('Mind Stone', 2, 0, 1),
    'orzhov signet': Card('Orzhov Signet', 2, 1, 2),
    'golgari signet': Card('Golgari Signet', 2, 1, 2),
    'selesnya signet': Card('Selesnya Signet', 2, 1, 2),
}
