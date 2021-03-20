from collections import namedtuple
from dataclasses import dataclass


class NonlandCard:
    def cast(self, state, remaining_mana):
        pass

    @property
    def fast(self):
        pass


@dataclass
class ManaPermanent(NonlandCard):
    name: str
    cmc: int
    input_cost: int
    payoff: int
    enters_tapped: bool

    @property
    def fast(self):
        return self.payoff > self.cmc + self.input_cost and self.enters_tapped == False

    def cast(self, state, remaining_mana):
        remaining_mana -= self.cmc
        production = self.payoff - self.input_cost
        if self.enters_tapped == 0 and remaining_mana >= self.input_cost:
            remaining_mana += production
        state.extra_mana_per_turn = state.extra_mana_per_turn + production
        return remaining_mana


@dataclass
class LandFetcher(NonlandCard):
    name: str
    cmc: int
    num_lands_to_play: int
    num_tapped_lands_to_play: int
    num_lands_to_hand: int
    num_lands_to_sac: int

    def cast(self, state, remaining_mana):
        assert remaining_mana >= self.cmc
        assert state.num_lands_in_play >= self.num_lands_to_sac
        remaining_mana -= self.cmc
        state.num_lands_in_play -= self.num_lands_to_sac

        state.num_lands_in_library -= self.num_lands_to_play
        state.num_lands_in_play += self.num_lands_to_play
        remaining_mana += self.num_lands_to_play

        state.num_lands_in_library -= self.num_tapped_lands_to_play
        state.num_lands_in_play += self.num_tapped_lands_to_play

        state.num_lands_in_library -= self.num_lands_to_hand
        state.num_lands_in_hand += self.num_lands_to_hand

        return remaining_mana

    @property
    def fast(self):
        return False


@dataclass
class ExtraLands(NonlandCard):
    name: str
    cmc: int
    num_extra_lands: int

    def cast(self, state, remaining_mana):
        assert remaining_mana >= self.cmc
        remaining_mana -= self.cmc
        state.lands_per_turn += self.num_extra_lands

        num_immediate_lands = min(self.num_extra_lands,
                                  state.num_lands_in_hand)
        state.num_lands_in_play += num_immediate_lands
        state.num_lands_in_hand -= num_immediate_lands
        remaining_mana += num_immediate_lands
        return remaining_mana

    @property
    def fast(self):
        return False

# pylint: disable=line-too-long
# yapf: disable
PRODUCERS = {
    # ARTIFACTS
    # Amazing things
    'Chrome Mox':  ManaPermanent(name='Chrome Mox',  cmc=0, input_cost=0, payoff=1, enters_tapped=False),
    'Mana Crypt':  ManaPermanent(name='Mana Crypt',  cmc=0, input_cost=0, payoff=2, enters_tapped=False),
    'Mox Diamond': ManaPermanent(name='Mox Diamond', cmc=0, input_cost=0, payoff=1, enters_tapped=False),
    'Mox Opal':    ManaPermanent(name='Mox Opal',    cmc=0, input_cost=0, payoff=1, enters_tapped=False),
    'Sol Ring':    ManaPermanent(name='Sol Ring',    cmc=1, input_cost=0, payoff=2, enters_tapped=False),

    # Diamonds
    'Charcoal Diamond': ManaPermanent(name='Charcoal Diamond', cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Fire Diamond':     ManaPermanent(name='Fire Diamond',     cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Marble Diamond':   ManaPermanent(name='Marble Diamond',   cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Moss Diamond':     ManaPermanent(name='Moss Diamond',     cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Sky Diamond':      ManaPermanent(name='Sky Diamond',      cmc=2, input_cost=0, payoff=1, enters_tapped=True),

    # 2 For 1s
    'Mind Stone':      ManaPermanent(name='Mind Stone',      cmc=2, input_cost=0, payoff=1, enters_tapped=False),
    'Thought Vessel':  ManaPermanent(name='Thought Vessel',  cmc=2, input_cost=0, payoff=1, enters_tapped=False),

    # Signets
    'Arcane Signet':   ManaPermanent(name='Arcane Signet',   cmc=2, input_cost=0, payoff=1, enters_tapped=False),
    'Azorius Signet':  ManaPermanent(name='Azorius Signet',  cmc=2, input_cost=1, payoff=2, enters_tapped=False),
    'Boros Signet':    ManaPermanent(name='Boros Signet',    cmc=2, input_cost=1, payoff=2, enters_tapped=False),
    'Dimir Signet':    ManaPermanent(name='Dimir Signet',    cmc=2, input_cost=1, payoff=2, enters_tapped=False),
    'Golgari Signet':  ManaPermanent(name='Golgari Signet',  cmc=2, input_cost=1, payoff=2, enters_tapped=False),
    'Gruul Signet':    ManaPermanent(name='Gruul Signet',    cmc=2, input_cost=1, payoff=2, enters_tapped=False),
    'Izzet Signet':    ManaPermanent(name='Izzet Signet',    cmc=2, input_cost=1, payoff=2, enters_tapped=False),
    'Orzhov Signet':   ManaPermanent(name='Orzhov Signet',   cmc=2, input_cost=1, payoff=2, enters_tapped=False),
    'Rakdos Signet':   ManaPermanent(name='Rakdos Signet',   cmc=2, input_cost=1, payoff=2, enters_tapped=False),
    'Selesnya Signet': ManaPermanent(name='Selesnya Signet', cmc=2, input_cost=1, payoff=2, enters_tapped=False),
    'Simic Signet':    ManaPermanent(name='Simic Signet',    cmc=2, input_cost=1, payoff=2, enters_tapped=False),

    # Talisman
    'Talisman of Conviction': ManaPermanent(name='Talisman of Conviction', cmc=2, input_cost=0, payoff=1, enters_tapped=False),
    'Talisman of Creativity': ManaPermanent(name='Talisman of Creativity', cmc=2, input_cost=0, payoff=1, enters_tapped=False),
    'Talisman of Curiosity':  ManaPermanent(name='Talisman of Curiosity',  cmc=2, input_cost=0, payoff=1, enters_tapped=False),
    'Talisman of Dominance':  ManaPermanent(name='Talisman of Dominance',  cmc=2, input_cost=0, payoff=1, enters_tapped=False),
    'Talisman of Hierarchy':  ManaPermanent(name='Talisman of Hierarchy',  cmc=2, input_cost=0, payoff=1, enters_tapped=False),
    'Talisman of Impulse':    ManaPermanent(name='Talisman of Impulse',    cmc=2, input_cost=0, payoff=1, enters_tapped=False),
    'Talisman of Indulgence': ManaPermanent(name='Talisman of Indulgence', cmc=2, input_cost=0, payoff=1, enters_tapped=False),
    'Talisman of Progress':   ManaPermanent(name='Talisman of Progress',   cmc=2, input_cost=0, payoff=1, enters_tapped=False),
    'Talisman of Resilience': ManaPermanent(name='Talisman of Resilience', cmc=2, input_cost=0, payoff=1, enters_tapped=False),
    'Talisman of Unity':      ManaPermanent(name='Talisman of Unity',      cmc=2, input_cost=0, payoff=1, enters_tapped=False),

    # Lockets
    'Azorius Locket':  ManaPermanent(name='Azorius Locket',  cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Boros Locket':    ManaPermanent(name='Boros Locket',    cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Dimir Locket':    ManaPermanent(name='Dimir Locket',    cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Golgari Locket':  ManaPermanent(name='Golgari Locket',  cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Gruul Locket':    ManaPermanent(name='Gruul Locket',    cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Izzet Locket':    ManaPermanent(name='Izzet Locket',    cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Orzhov Locket':   ManaPermanent(name='Orzhov Locket',   cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Rakdos Locket':   ManaPermanent(name='Rakdos Locket',   cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Selesnya Locket': ManaPermanent(name='Selesnya Locket', cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Simic Locket':    ManaPermanent(name='Simic Locket',    cmc=3, input_cost=0, payoff=1, enters_tapped=False),

    'Obelisk of Bant':   ManaPermanent(name='Obelisk of Bant',   cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Obelisk of Esper':  ManaPermanent(name='Obelisk of Esper',  cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Obelisk of Grixis': ManaPermanent(name='Obelisk of Grixis', cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Obelisk of Jund':   ManaPermanent(name='Obelisk of Jund',   cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Obelisk of Naya':   ManaPermanent(name='Obelisk of Naya',   cmc=3, input_cost=0, payoff=1, enters_tapped=False),

    'Chromatic Lantern':      ManaPermanent(name='Chromatic Lantern',      cmc=3, input_cost=1, payoff=1, enters_tapped=False),
    'Vessel of Endless Rest': ManaPermanent(name='Vessel of Endless Rest', cmc=3, input_cost=1, payoff=1, enters_tapped=False),

    'Worn Powerstone': ManaPermanent(name='Worn Powerstone', cmc=3, input_cost=0, payoff=2, enters_tapped=True),

    'Hedron Archive': ManaPermanent(name='Hedron Archive', cmc=4, input_cost=0, payoff=2, enters_tapped=False),

    'Thran Dynamo': ManaPermanent(name='Thran Dynamo', cmc=4, input_cost=0, payoff=3, enters_tapped=False),

    # 1 MANA DORKS
    'Arbor Elf':            ManaPermanent(name='Arbor Elf',            cmc=1, input_cost=0, payoff=1, enters_tapped=True),
    'Avacyn\'s Pilgrim':    ManaPermanent(name='Avacyn\'s Pilgrim',    cmc=1, input_cost=0, payoff=1, enters_tapped=True),
    'Birds of Paradise':    ManaPermanent(name='Birds of Paradise',    cmc=1, input_cost=0, payoff=1, enters_tapped=True),
    'Boreal Druid':         ManaPermanent(name='Boreal Druid',         cmc=1, input_cost=0, payoff=1, enters_tapped=True),
    'Elvish Mystic':        ManaPermanent(name='Elvish Mystic',        cmc=1, input_cost=0, payoff=1, enters_tapped=True),
    'Elves of Deep Shadow': ManaPermanent(name='Elves of Deep Shadow', cmc=1, input_cost=0, payoff=1, enters_tapped=True),
    'Fyndhorn Elves':       ManaPermanent(name='Fyndhorn Elves',       cmc=1, input_cost=0, payoff=1, enters_tapped=True),
    'Llanowar Elves':       ManaPermanent(name='Llanowar Elves',       cmc=1, input_cost=0, payoff=1, enters_tapped=True),

    # 2 MANA DORKS
    'Paradise Druid': ManaPermanent(name='Paradise Druid', cmc=2, input_cost=0, payoff=1, enters_tapped=True),

    # ENCHANTMENTS
    'Wild Growth':      ManaPermanent(name='Wild Growth',      cmc=1, input_cost=0, payoff=1, enters_tapped=True),
    'Utopia Sprawl':    ManaPermanent(name='Utopia Sprawl',    cmc=1, input_cost=0, payoff=1, enters_tapped=True),
    'Fertile Ground':   ManaPermanent(name='Fertile Ground',   cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Wolfwillow Haven': ManaPermanent(name='Wolfwillow Haven', cmc=2, input_cost=0, payoff=1, enters_tapped=True),

    # LAND FETCHERS
    # 2 CMC
    'Rampant Growth': LandFetcher(name='Rampant Growth', cmc=2, num_lands_to_play=0, num_tapped_lands_to_play=1, num_lands_to_hand=0, num_lands_to_sac=0),

    # 3 CMC
    'Cultivate':       LandFetcher(name='Cultivate', cmc=3, num_lands_to_play=0, num_tapped_lands_to_play=1, num_lands_to_hand=1, num_lands_to_sac=0),
    'Harrow':          LandFetcher(name='Harrow',    cmc=3, num_lands_to_play=2, num_tapped_lands_to_play=0, num_lands_to_hand=0, num_lands_to_sac=1),
    'Kodama\'s Reach': LandFetcher(name='Cultivate', cmc=3, num_lands_to_play=0, num_tapped_lands_to_play=1, num_lands_to_hand=1, num_lands_to_sac=0),

    # 4 CMC
    'Circuitious Route': LandFetcher(name='Circuitous Route', cmc=4, num_lands_to_play=0, num_tapped_lands_to_play=2, num_lands_to_hand=0, num_lands_to_sac=0),
    'Skyshround Claim':  LandFetcher(name='Skyshroud Claim',  cmc=4, num_lands_to_play=2, num_tapped_lands_to_play=0, num_lands_to_hand=0, num_lands_to_sac=0),

    # EXTRA LANDS
    'Azusa, Lost but Seeking':    ExtraLands(name='Azusa, Lost but Seeking',    cmc=3, num_extra_lands=2),
    'Dryad of the Ilysian Grove': ExtraLands(name='Dryad of the Ilysian Grove', cmc=3, num_extra_lands=1),
    'Ghirapur Orrery':            ExtraLands(name='Ghirapur Orrery',            cmc=4, num_extra_lands=1),
    'Exploration':                ExtraLands(name='Exploration',                cmc=1, num_extra_lands=1),
    'Wayward Swordtooth':         ExtraLands(name='Wayward Swordtooth',         cmc=3, num_extra_lands=1),
}
# yapf: enable
