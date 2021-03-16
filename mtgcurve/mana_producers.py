from collections import namedtuple

Card = namedtuple('Card', [
    'name',
    'cmc',
    'input_cost',
    'payoff',
    'turns_til_active',
])

PRODUCERS = {
    ### ARTIFACTS

    # Amazing things
    'Chrome Mox':  Card(name='Chrome Mox',  cmc=0, input_cost=0, payoff=1, turns_til_active=0),
    'Mana Crypt':  Card(name='Mana Crypt',  cmc=0, input_cost=0, payoff=2, turns_til_active=0),
    'Mox Diamond': Card(name='Mox Diamond', cmc=0, input_cost=0, payoff=1, turns_til_active=0),
    'Mox Opal':    Card(name='Mox Opal',    cmc=0, input_cost=0, payoff=1, turns_til_active=0),
    'Sol Ring':    Card(name='Sol Ring',    cmc=1, input_cost=0, payoff=2, turns_til_active=0),

    # Diamonds
    'Charcoal Diamond': Card(name='Charcoal Diamond', cmc=2, input_cost=0, payoff=1, turns_til_active=1),
    'Fire Diamond':     Card(name='Fire Diamond',     cmc=2, input_cost=0, payoff=1, turns_til_active=1),
    'Marble Diamond':   Card(name='Marble Diamond',   cmc=2, input_cost=0, payoff=1, turns_til_active=1),
    'Moss Diamond':     Card(name='Moss Diamond',     cmc=2, input_cost=0, payoff=1, turns_til_active=1),
    'Sky Diamond':      Card(name='Sky Diamond',      cmc=2, input_cost=0, payoff=1, turns_til_active=1),

    # 2 For 1s
    'Mind Stone':      Card(name='Mind Stone',      cmc=2, input_cost=0, payoff=1, turns_til_active=0),

    # Signets
    'Arcane Signet':   Card(name='Arcane Signet',   cmc=2, input_cost=0, payoff=1, turns_til_active=0),
    'Azorius Signet':  Card(name='Azorius Signet',  cmc=2, input_cost=1, payoff=2, turns_til_active=0),
    'Boros Signet':    Card(name='Boros Signet',    cmc=2, input_cost=1, payoff=2, turns_til_active=0),
    'Dimir Signet':    Card(name='Dimir Signet',    cmc=2, input_cost=1, payoff=2, turns_til_active=0),
    'Golgari Signet':  Card(name='Golgari Signet',  cmc=2, input_cost=1, payoff=2, turns_til_active=0),
    'Gruul Signet':    Card(name='Gruul Signet',    cmc=2, input_cost=1, payoff=2, turns_til_active=0),
    'Izzet Signet':    Card(name='Izzet Signet',    cmc=2, input_cost=1, payoff=2, turns_til_active=0),
    'Orzhov Signet':   Card(name='Orzhov Signet',   cmc=2, input_cost=1, payoff=2, turns_til_active=0),
    'Rakdos Signet':   Card(name='Rakdos Signet',   cmc=2, input_cost=1, payoff=2, turns_til_active=0),
    'Selesnya Signet': Card(name='Selesnya Signet', cmc=2, input_cost=1, payoff=2, turns_til_active=0),
    'Simic Signet':    Card(name='Simic Signet',    cmc=2, input_cost=1, payoff=2, turns_til_active=0),

    # Talisman
    'Talisman of Conviction': Card(name='Talisman of Conviction', cmc=2, input_cost=0, payoff=1, turns_til_active=0),
    'Talisman of Creativity': Card(name='Talisman of Creativity', cmc=2, input_cost=0, payoff=1, turns_til_active=0),
    'Talisman of Curiosity':  Card(name='Talisman of Curiosity',  cmc=2, input_cost=0, payoff=1, turns_til_active=0),
    'Talisman of Dominance':  Card(name='Talisman of Dominance',  cmc=2, input_cost=0, payoff=1, turns_til_active=0),
    'Talisman of Hierarchy':  Card(name='Talisman of Hierarchy',  cmc=2, input_cost=0, payoff=1, turns_til_active=0),
    'Talisman of Impulse':    Card(name='Talisman of Impulse',    cmc=2, input_cost=0, payoff=1, turns_til_active=0),
    'Talisman of Indulgence': Card(name='Talisman of Indulgence', cmc=2, input_cost=0, payoff=1, turns_til_active=0),
    'Talisman of Progress':   Card(name='Talisman of Progress',   cmc=2, input_cost=0, payoff=1, turns_til_active=0),
    'Talisman of Resilience': Card(name='Talisman of Resilience', cmc=2, input_cost=0, payoff=1, turns_til_active=0),
    'Talisman of Unity':      Card(name='Talisman of Unity',      cmc=2, input_cost=0, payoff=1, turns_til_active=0),

    # Lockets
    'Azorius Locket':  Card(name='Azorius Locket',  cmc=3, input_cost=1, payoff=1, turns_til_active=0),
    'Boros Locket':    Card(name='Boros Locket',    cmc=3, input_cost=1, payoff=1, turns_til_active=0),
    'Dimir Locket':    Card(name='Dimir Locket',    cmc=3, input_cost=1, payoff=1, turns_til_active=0),
    'Golgari Locket':  Card(name='Golgari Locket',  cmc=3, input_cost=1, payoff=1, turns_til_active=0),
    'Gruul Locket':    Card(name='Gruul Locket',    cmc=3, input_cost=1, payoff=1, turns_til_active=0),
    'Izzet Locket':    Card(name='Izzet Locket',    cmc=3, input_cost=1, payoff=1, turns_til_active=0),
    'Orzhov Locket':   Card(name='Orzhov Locket',   cmc=3, input_cost=1, payoff=1, turns_til_active=0),
    'Rakdos Locket':   Card(name='Rakdos Locket',   cmc=3, input_cost=1, payoff=1, turns_til_active=0),
    'Selesnya Locket': Card(name='Selesnya Locket', cmc=3, input_cost=1, payoff=1, turns_til_active=0),
    'Simic Locket':    Card(name='Simic Locket',    cmc=3, input_cost=1, payoff=1, turns_til_active=0),

    ### 1 MANA DORKS
    'Arbor Elf':            Card(name='Arbor Elf',            cmc=1, input_cost=0, payoff=1, turns_til_active=1),
    'Avacyn\'s Pilgrim':    Card(name='Avacy\'s Pilgrim',     cmc=1, input_cost=0, payoff=1, turns_til_active=1),
    'Elvish Mystic':        Card(name='Elvish Mystic',        cmc=1, input_cost=0, payoff=1, turns_til_active=1),
    'Elves of Deep Shadow': Card(name='Elves of Deep Shadow', cmc=1, input_cost=0, payoff=1, turns_til_active=1),
    'Fyndhorn Elves':       Card(name='Fyndhorn Elves',       cmc=1, input_cost=0, payoff=1, turns_til_active=1),
    'Llanowar Elves':       Card(name='Llanowar Elves',       cmc=1, input_cost=0, payoff=1, turns_til_active=1),

    ### 2 MANA DORKS
    'Paradise Druid': Card(name='Paradise Druid', cmc=2, input_cost=0, payoff=1, turns_til_active=1),

    ### ENCHANTMENTS
    'Wild Growth': Card(name='Wild Growth', cmc=1, input_cost=0, payoff=1, turns_til_active=1), # Need to make lands_til_active
}
