from collections import namedtuple
from dataclasses import dataclass


class NonlandCard:
    def cast(self, state, remaining_mana):
        pass

    def ramp(self, state):
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

    def ramp(self, state):
        return self.payoff

    @property
    def fast(self):
        return self.payoff > self.cmc + self.input_cost and not self.enters_tapped

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
    num_lands_to_play: int = 0
    num_tapped_lands_to_play: int = 0
    num_lands_to_hand: int = 0
    num_lands_to_sac: int = 0

    def ramp(self, state):
        return self.num_lands_to_play + self.num_tapped_lands_to_play - self.num_lands_to_sac

    @property
    def fast(self):
        return False

    def cast(self, state, remaining_mana):
        assert remaining_mana >= self.cmc
        assert state.num_lands_in_play >= self.num_lands_to_sac
        remaining_mana -= self.cmc
        state.num_lands_in_play -= self.num_lands_to_sac

        state.num_cards_in_library -= self.num_lands_to_play
        state.num_lands_in_library -= self.num_lands_to_play
        state.num_lands_in_play += self.num_lands_to_play
        remaining_mana += self.num_lands_to_play

        state.num_cards_in_library -= self.num_tapped_lands_to_play
        state.num_lands_in_library -= self.num_tapped_lands_to_play
        state.num_lands_in_play += self.num_tapped_lands_to_play

        state.num_cards_in_library -= self.num_lands_to_hand
        state.num_lands_in_library -= self.num_lands_to_hand
        state.num_lands_in_hand += self.num_lands_to_hand

        return remaining_mana


@dataclass
class ExtraLands(NonlandCard):
    name: str
    cmc: int
    num_extra_lands: int

    def ramp(self, state):
        return min(self.num_extra_lands, state.num_lands_in_hand)

    @property
    def fast(self):
        return False

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


@dataclass
class SacPermanent(NonlandCard):
    name: str
    cmc: int
    activation_cost: int = 0
    num_lands_to_play: int = 0
    num_tapped_lands_to_play: int = 0
    num_lands_to_hand: int = 0

    def ramp(self, state):
        return self.num_lands_to_play + self.num_tapped_lands_to_play

    @property
    def fast(self):
        return False

    def cast(self, state, remaining_mana):
        assert remaining_mana >= self.cmc
        remaining_mana -= self.cmc

        if self.name not in state.activatable_permanents:
            state.activatable_permanents[self.name] = 0
        state.activatable_permanents[self.name] += 1
        return remaining_mana

    def activate(self, state, remaining_mana):
        assert remaining_mana >= self.activation_cost
        remaining_mana -= self.activation_cost

        state.num_cards_in_library -= self.num_lands_to_play
        state.num_lands_in_library -= self.num_lands_to_play
        state.num_lands_in_play += self.num_lands_to_play
        remaining_mana += self.num_lands_to_play

        state.num_cards_in_library -= self.num_tapped_lands_to_play
        state.num_lands_in_library -= self.num_tapped_lands_to_play
        state.num_lands_in_play += self.num_tapped_lands_to_play

        state.num_cards_in_library -= self.num_lands_to_hand
        state.num_lands_in_library -= self.num_lands_to_hand
        state.num_lands_in_hand += self.num_lands_to_hand

        state.activatable_permanents[self.name] -= 1
        return remaining_mana


# pylint: disable=line-too-long
# yapf: disable
PRODUCERS = {
    # ARTIFACTS
    # Amazing things
    'Chrome Mox':  ManaPermanent(name='Chrome Mox',  cmc=0, input_cost=0, payoff=1, enters_tapped=False),
    'Mana Crypt':  ManaPermanent(name='Mana Crypt',  cmc=0, input_cost=0, payoff=2, enters_tapped=False),
    'Mox Amber':   ManaPermanent(name='Mox Amber',   cmc=0, input_cost=0, payoff=1, enters_tapped=False),
    'Mox Diamond': ManaPermanent(name='Mox Diamond', cmc=0, input_cost=0, payoff=1, enters_tapped=False),
    'Mox Opal':    ManaPermanent(name='Mox Opal',    cmc=0, input_cost=0, payoff=1, enters_tapped=False),
    'Sol Ring':    ManaPermanent(name='Sol Ring',    cmc=1, input_cost=0, payoff=2, enters_tapped=False),

    # Diamonds
    'Charcoal Diamond': ManaPermanent(name='Charcoal Diamond', cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Fire Diamond':     ManaPermanent(name='Fire Diamond',     cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Marble Diamond':   ManaPermanent(name='Marble Diamond',   cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Moss Diamond':     ManaPermanent(name='Moss Diamond',     cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Sky Diamond':      ManaPermanent(name='Sky Diamond',      cmc=2, input_cost=0, payoff=1, enters_tapped=True),

    'Coldsteel Heart':  ManaPermanent(name='Coldsteel Heart',  cmc=2, input_cost=0, payoff=1, enters_tapped=True),

    # 2 For 1s
    'Fellwar Stone':        ManaPermanent(name='Fellwar Stone',        cmc=2, input_cost=0, payoff=1, enters_tapped=False),
    'Fractured Powerstone': ManaPermanent(name='Fractured Powerstone', cmc=2, input_cost=0, payoff=1, enters_tapped=False),
    'Mind Stone':           ManaPermanent(name='Mind Stone',           cmc=2, input_cost=0, payoff=1, enters_tapped=False),
    'Prismatic Lens':       ManaPermanent(name='Prismatic Lens',       cmc=2, input_cost=0, payoff=1, enters_tapped=False),
    'Pristine Talisman':    ManaPermanent(name='Pristine Talisman',       cmc=2, input_cost=0, payoff=1, enters_tapped=False),
    'Thought Vessel':       ManaPermanent(name='Thought Vessel',       cmc=2, input_cost=0, payoff=1, enters_tapped=False),

    'Corrupted Grafstone': ManaPermanent(name='Corrupted Grafstone', cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Guardian Idol':       ManaPermanent(name='Guardian Idol',       cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Star Compass':        ManaPermanent(name='Star Compass',        cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Sphere of the Suns':  ManaPermanent(name='Sphere of the Suns',  cmc=2, input_cost=0, payoff=1, enters_tapped=True),

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

    'Azorius Cluestone':  ManaPermanent(name='Azorius Cluestone',  cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Boros Cluestone':    ManaPermanent(name='Boros Cluestone',    cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Dimir Cluestone':    ManaPermanent(name='Dimir Cluestone',    cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Golgari Cluestone':  ManaPermanent(name='Golgari Cluestone',  cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Gruul Cluestone':    ManaPermanent(name='Gruul Cluestone',    cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Izzet Cluestone':    ManaPermanent(name='Izzet Cluestone',    cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Orzhov Cluestone':   ManaPermanent(name='Orzhov Cluestone',   cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Rakdos Cluestone':   ManaPermanent(name='Rakdos Cluestone',   cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Selesnya Cluestone': ManaPermanent(name='Selesnya Cluestone', cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Simic Cluestone':    ManaPermanent(name='Simic Cluestone',    cmc=3, input_cost=0, payoff=1, enters_tapped=False),

    'Azorius Keyrune':  ManaPermanent(name='Azorius Keyrune',  cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Boros Keyrune':    ManaPermanent(name='Boros Keyrune',    cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Dimir Keyrune':    ManaPermanent(name='Dimir Keyrune',    cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Golgari Keyrune':  ManaPermanent(name='Golgari Keyrune',  cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Gruul Keyrune':    ManaPermanent(name='Gruul Keyrune',    cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Izzet Keyrune':    ManaPermanent(name='Izzet Keyrune',    cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Orzhov Keyrune':   ManaPermanent(name='Orzhov Keyrune',   cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Rakdos Keyrune':   ManaPermanent(name='Rakdos Keyrune',   cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Selesnya Keyrune': ManaPermanent(name='Selesnya Keyrune', cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Simic Keyrune':    ManaPermanent(name='Simic Keyrune',    cmc=3, input_cost=0, payoff=1, enters_tapped=False),

    'Obelisk of Bant':   ManaPermanent(name='Obelisk of Bant',   cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Obelisk of Esper':  ManaPermanent(name='Obelisk of Esper',  cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Obelisk of Grixis': ManaPermanent(name='Obelisk of Grixis', cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Obelisk of Jund':   ManaPermanent(name='Obelisk of Jund',   cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Obelisk of Naya':   ManaPermanent(name='Obelisk of Naya',   cmc=3, input_cost=0, payoff=1, enters_tapped=False),

    'Abzan Banner':    ManaPermanent(name='Abzan Banner',    cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Heraldic Banner': ManaPermanent(name='Heraldic Banner', cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Jeskai Banner':   ManaPermanent(name='Jeskai Banner',   cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Mardu Banner':    ManaPermanent(name='Mardu Banner',    cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Sultai Banner':   ManaPermanent(name='Sultai Banner',   cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Temur Banner':    ManaPermanent(name='Temur Banner',    cmc=3, input_cost=0, payoff=1, enters_tapped=False),

    'Atarka Monument':   ManaPermanent(name='Atarka Monument',   cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Dromoka Monument':  ManaPermanent(name='Dromoka Monument',  cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Kolaghan Monument': ManaPermanent(name='Kolaghan Monument', cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Ojutai Monument':   ManaPermanent(name='Ojutai Monument',   cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Silumgar Monument': ManaPermanent(name='Silumgar Monument', cmc=3, input_cost=0, payoff=1, enters_tapped=False),

    # 'Cryptolith Fragment':  ManaPermanent(name='Cryptolith Fragment',  cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Fieldmist Borderpost': ManaPermanent(name='Fieldmist Borderpost', cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Firewild Borderpost':  ManaPermanent(name='Firewild Borderpost',  cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Mistvein Borderpost':  ManaPermanent(name='Mistvein Borderpost',  cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Veinfire Borderpost':  ManaPermanent(name='Veinfire Borderpost',  cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Wildfield Borderpost': ManaPermanent(name='Wildfield Borderpost', cmc=3, input_cost=0, payoff=1, enters_tapped=True),

    'Indatha Crystal': ManaPermanent(name='Indatha Crystal',  cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Ketria Crystal':  ManaPermanent(name='Ketria Crystal',  cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Raugrin Crystal': ManaPermanent(name='Raugrin Crystal', cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Savai Crystal':   ManaPermanent(name='Savai Crystal',   cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Zagoth Crystal':  ManaPermanent(name='Zagoth Crystal',  cmc=3, input_cost=0, payoff=1, enters_tapped=False),

    'Eye of Ramos':   ManaPermanent(name='Eye of Ramos',   cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Heart of Ramos': ManaPermanent(name='Heart of Ramos', cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Horn of Ramos':  ManaPermanent(name='Horn of Ramos',  cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Skull of Ramos': ManaPermanent(name='Skull of Ramos', cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Tooth of Ramos': ManaPermanent(name='Tooth of Ramos', cmc=3, input_cost=0, payoff=1, enters_tapped=False),

    'Bloodstone Cameo':  ManaPermanent(name='Bloodstone Cameo',  cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Drake-Skull Cameo': ManaPermanent(name='Drake-Skull Cameo', cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Seashell Cameo':    ManaPermanent(name='Seashell Cameo',    cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Tigereye Cameo':    ManaPermanent(name='Tigereye Cameo',    cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Troll-Horn Cameo':  ManaPermanent(name='Troll-Horn Cameo',  cmc=3, input_cost=0, payoff=1, enters_tapped=False),

    'Bonder\'s Ornament':     ManaPermanent(name='Bonder\'s Ornament',     cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Chromatic Lantern':      ManaPermanent(name='Chromatic Lantern',      cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Coalition Relic':        ManaPermanent(name='Coalition Relic',        cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Commander\'s Sphere':    ManaPermanent(name='Commander\'s Sphere',    cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Darksteel Ingot':        ManaPermanent(name='Darksteel Ingot',        cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Fountain of Ichor':      ManaPermanent(name='Fountain of Ichor',      cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Hierophant\'s Chalice':  ManaPermanent(name='Hierophant\'s Chalice',  cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Honor-Worn Shaku':       ManaPermanent(name='Honor-Worn Shaku',       cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Magnifying Glass':       ManaPermanent(name='Magnifying Glass',       cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Mana Geode':             ManaPermanent(name='Mana Geode',             cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Manalith':               ManaPermanent(name='Manalith',               cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Mana Prism':             ManaPermanent(name='Mana Prism',             cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Midnight Clock':         ManaPermanent(name='Midnight Clock',         cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Phyrexian Lens':         ManaPermanent(name='Phyrexian Lens',         cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Phyrexian Totem':        ManaPermanent(name='Phyrexian Totem',        cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Powerstone Shard':       ManaPermanent(name='Powerstone Shard',       cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Seer\'s Lantern':        ManaPermanent(name='Seer\'s Lantern',        cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Serum Powder':           ManaPermanent(name='Serum Powder',           cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Skyclave Relic':         ManaPermanent(name='Skyclave Relic',         cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Sol Grail':              ManaPermanent(name='Sol Grail',              cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Spectral Searchlight':   ManaPermanent(name='Spectral Searchlight',   cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Spinning Wheel':         ManaPermanent(name='Spinning Wheel',         cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Thunder Totem':          ManaPermanent(name='Thunder Totem',          cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Unstable Obelisk':       ManaPermanent(name='Unstable Obelisk',       cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Vessel of Endless Rest': ManaPermanent(name='Vessel of Endless Rest', cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Victory Chimes':         ManaPermanent(name='Victory Chimes',         cmc=3, input_cost=0, payoff=1, enters_tapped=False),

    # Larger Artifacts
    'Worn Powerstone':   ManaPermanent(name='Worn Powerstone',   cmc=3, input_cost=0, payoff=2, enters_tapped=True),

    'Firemind Vessel':   ManaPermanent(name='Firemind Vessel',   cmc=4, input_cost=0, payoff=2, enters_tapped=True),
    'Hedron Archive':    ManaPermanent(name='Hedron Archive',    cmc=4, input_cost=0, payoff=2, enters_tapped=False),
    'Sisay\'s Ring':     ManaPermanent(name='Sisay\'s Ring',     cmc=4, input_cost=0, payoff=2, enters_tapped=False),
    'Thran Dynamo':      ManaPermanent(name='Thran Dynamo',      cmc=4, input_cost=0, payoff=3, enters_tapped=False),
    'Ur-Golem\'s Eye':   ManaPermanent(name='Ur-Golem\'s Eye',   cmc=4, input_cost=0, payoff=2, enters_tapped=False),
    'Visage of Bolas':   ManaPermanent(name='Visage of Bolas',   cmc=4, input_cost=0, payoff=1, enters_tapped=False),

    'Gilded Lotus':          ManaPermanent(name='Gilded Lotus',          cmc=5, input_cost=0, payoff=3, enters_tapped=False),
    'Meteorite':             ManaPermanent(name='Meteorite',             cmc=5, input_cost=0, payoff=1, enters_tapped=False),
    'Tome of the Guildpact': ManaPermanent(name='Tome of the Guildpact', cmc=5, input_cost=0, payoff=1, enters_tapped=False),

    'Coveted Jewel':     ManaPermanent(name='Coveted Jewel',     cmc=6, input_cost=0, payoff=3, enters_tapped=False),
    'Dreamstone Hedron': ManaPermanent(name='Dreamstone Hedron', cmc=6, input_cost=0, payoff=3, enters_tapped=False),

    # 1 MANA DORKS
    'Arbor Elf':            ManaPermanent(name='Arbor Elf',            cmc=1, input_cost=0, payoff=1, enters_tapped=True),
    'Avacyn\'s Pilgrim':    ManaPermanent(name='Avacyn\'s Pilgrim',    cmc=1, input_cost=0, payoff=1, enters_tapped=True),
    'Birds of Paradise':    ManaPermanent(name='Birds of Paradise',    cmc=1, input_cost=0, payoff=1, enters_tapped=True),
    'Boreal Druid':         ManaPermanent(name='Boreal Druid',         cmc=1, input_cost=0, payoff=1, enters_tapped=True),
    'Deathrite Shaman':     ManaPermanent(name='Deathrite Shaman',     cmc=1, input_cost=0, payoff=1, enters_tapped=True),
    'Elvish Mystic':        ManaPermanent(name='Elvish Mystic',        cmc=1, input_cost=0, payoff=1, enters_tapped=True),
    'Elves of Deep Shadow': ManaPermanent(name='Elves of Deep Shadow', cmc=1, input_cost=0, payoff=1, enters_tapped=True),
    'Fyndhorn Elves':       ManaPermanent(name='Fyndhorn Elves',       cmc=1, input_cost=0, payoff=1, enters_tapped=True),
    'Llanowar Elves':       ManaPermanent(name='Llanowar Elves',       cmc=1, input_cost=0, payoff=1, enters_tapped=True),
    'Noble Hierarch':       ManaPermanent(name='Noble Hierarch',       cmc=1, input_cost=0, payoff=1, enters_tapped=True),

    # 2 MANA DORKS
    'Bloom Tender':           ManaPermanent(name='Bloom Tender',           cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Deathcap Cultivator':    ManaPermanent(name='Deathcap Cultivator',    cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Devoted Druid':          ManaPermanent(name='Devoted Druid',          cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Druid of the Anima':     ManaPermanent(name='Druid of the Anima',     cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Druid of the Cowl':      ManaPermanent(name='Druid of the Cowl',      cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Elfhame Druid':          ManaPermanent(name='Elfhame Druid',          cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Golden Hind':            ManaPermanent(name='Golden Hind',            cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Harabaz Druid':          ManaPermanent(name='Harabaz Druid',          cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Harvester Druid':        ManaPermanent(name='Harvester Druid',        cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Heart Warden':           ManaPermanent(name='Heart Warden',           cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Hedron Crawler':         ManaPermanent(name='Hedron Crawler',         cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Ilysian Caryatid':       ManaPermanent(name='Ilysian Caryatid',       cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Incubation Druid':       ManaPermanent(name='Incubation Druid',       cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Leaf Gilder':            ManaPermanent(name='Leaf Gilder',            cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Leafkin Druid':          ManaPermanent(name='Leafkin Druid',          cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Llanowar Dead':          ManaPermanent(name='Llanowar Dead',          cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Magus of the Library':   ManaPermanent(name='Magus of the Library',   cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Manakin':                ManaPermanent(name='Manakin',                cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Manaweft Sliver':        ManaPermanent(name='Manaweft Sliver',        cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Maraleaf Pixie':         ManaPermanent(name='Maraleaf Pixie',         cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Millikin':               ManaPermanent(name='Millikin',               cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Overgrown Battlement':   ManaPermanent(name='Overgrown Battlement',   cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Paradise Druid':         ManaPermanent(name='Paradise Druid',         cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Plague Myr':             ManaPermanent(name='Plague Myr',             cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Priest of Titania':      ManaPermanent(name='Priest of Titania',      cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Quirion Elves':          ManaPermanent(name='Quirion Elves',          cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Quirion Explorer':       ManaPermanent(name='Quirion Explorer',       cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Radha, Heir to Keld':    ManaPermanent(name='Radha, Heir to Keld',    cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    # 'Rosethorn Acolyte':      ManaPermanent(name='Rosethorn Acolyte',      cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    # 'Scorned Villager':       ManaPermanent(name='Scorned Villager',       cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Sea Scryer':             ManaPermanent(name='Sea Scryer',             cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Skull Prophet':          ManaPermanent(name='Skull Prophet',          cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Skyshroud Elf':          ManaPermanent(name='Skyshroud Elf',          cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Steward of Valeron':     ManaPermanent(name='Steward of Valeron',     cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Sylvan Caryatid':        ManaPermanent(name='Sylvan Caryatid',        cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Sylvok Explorer':        ManaPermanent(name='Sylvok Explorer',        cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    # 'Ulvenwald Captive':      ManaPermanent(name='Ulvenwald Captive',      cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Urborg Elf':             ManaPermanent(name='Urborg Elf',             cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Utopia Tree':            ManaPermanent(name='Utopia Tree',            cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Vine Trellis':           ManaPermanent(name='Vine Trellis',           cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Werebear':               ManaPermanent(name='Werebear',               cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Whisperer of the Wilds': ManaPermanent(name='Whisperer of the Wilds', cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Wirewood Elf':           ManaPermanent(name='Wirewood Elf',           cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Woodland Mystic':        ManaPermanent(name='Woodland Mystic',        cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Zhur-Taa Druid':         ManaPermanent(name='Zhur-Taa Druid',         cmc=2, input_cost=0, payoff=1, enters_tapped=True),

    # 3 MANA DORKS
    'Alloy Myr':            ManaPermanent(name='Alloy Myr',            cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Axebane Guardian':     ManaPermanent(name='Axebane Guardian',     cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Copper Myr':           ManaPermanent(name='Copper Myr',           cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Draconic Disciple':    ManaPermanent(name='Draconic Disciple',    cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Elvish Archdruid':     ManaPermanent(name='Elvish Archdruid',     cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Elvish Harbinger':     ManaPermanent(name='Elvish Harbinger',     cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Gold Myr':             ManaPermanent(name='Gold Myr',             cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Iron Myr':             ManaPermanent(name='Iron Myr',             cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Leaden Myr':           ManaPermanent(name='Leaden Myr',           cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Leyline Prowler':      ManaPermanent(name='Leyline Prowler',      cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Lifespring Druid':     ManaPermanent(name='Lifespring Druid',     cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Llanowar Visionary':   ManaPermanent(name='Llanowar Visionary',   cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Lullmage\'s Familiar': ManaPermanent(name='Lullmage\'s Familiar', cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Opaline Unicorn':      ManaPermanent(name='Opaline Unicorn',      cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Orazca Relic':         ManaPermanent(name='Orazca Relic',         cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Scuttlemutt':          ManaPermanent(name='Scuttlemutt',          cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Silhana Starfletcher': ManaPermanent(name='Silhana Starfletcher', cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Silver Myr':           ManaPermanent(name='Silver Myr',           cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Sisters of the Flame': ManaPermanent(name='Sisters of the Flame', cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Viridian Joiner':      ManaPermanent(name='Viridian Joiner',      cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Warden of the Wall':   ManaPermanent(name='Warden of the Wall',   cmc=3, input_cost=0, payoff=1, enters_tapped=True),

    'Apprentice Wizard':  ManaPermanent(name='Apprentice Wizard',  cmc=3, input_cost=1, payoff=3, enters_tapped=True),
    'Greenweaver Druid':  ManaPermanent(name='Greenweaver Druid',  cmc=3, input_cost=0, payoff=2, enters_tapped=True),
    'Gyre Engineer':      ManaPermanent(name='Gyre Engineer',      cmc=3, input_cost=0, payoff=2, enters_tapped=True),
    'Faeburrow Elder':    ManaPermanent(name='Faeburrow Elder',    cmc=3, input_cost=0, payoff=2, enters_tapped=True),
    'Llanowar Tribe':     ManaPermanent(name='Llanowar Tribe',     cmc=3, input_cost=0, payoff=3, enters_tapped=True),
    'Nantuko Elder':      ManaPermanent(name='Nantuko Elder',      cmc=3, input_cost=0, payoff=2, enters_tapped=True),
    'Palladium Myr':      ManaPermanent(name='Palladium Myr',      cmc=3, input_cost=0, payoff=2, enters_tapped=True),
    'Weaver of Currents': ManaPermanent(name='Weaver of Currents', cmc=3, input_cost=0, payoff=2, enters_tapped=True),

    # 4 MANA DORKS
    'Canopy Tactician':        ManaPermanent(name='Canopy Tactician',        cmc=4, input_cost=0, payoff=3, enters_tapped=True),
    'Drumhunter':              ManaPermanent(name='Drumhunter',              cmc=4, input_cost=0, payoff=1, enters_tapped=True),
    'Leafkin Avenger':         ManaPermanent(name='Leafkin Avenger',         cmc=4, input_cost=0, payoff=1, enters_tapped=True),
    'Skyshroud Troopers':      ManaPermanent(name='Skyshroud Troopers',      cmc=4, input_cost=0, payoff=1, enters_tapped=True),
    'Warden of Geometries':    ManaPermanent(name='Warden of Geometries',    cmc=4, input_cost=0, payoff=1, enters_tapped=True),
    'Wirewood Channeler':      ManaPermanent(name='Wirewood Channeler',      cmc=4, input_cost=0, payoff=1, enters_tapped=True),
    'Yurlok of Scorch Thrash': ManaPermanent(name='Yurlok of Scorch Thrash', cmc=4, input_cost=1, payoff=3, enters_tapped=True),
    'Zaxara, the Exemplary':   ManaPermanent(name='Zaxara, the Exemplary',   cmc=4, input_cost=0, payoff=2, enters_tapped=True),

    # 5 MANA DORKS
    'Sunastian Falconer': ManaPermanent(name='Sunastian Falconer', cmc=5, input_cost=0, payoff=2, enters_tapped=True),

    # 6 MANA DORKS
    'Elvish Aberration': ManaPermanent(name='Elvish Aberration', cmc=6, input_cost=0, payoff=3, enters_tapped=True),

    # ENCHANTMENTS
    'Fertile Ground':   ManaPermanent(name='Fertile Ground',   cmc=2, input_cost=0, payoff=1, enters_tapped=True),
    'Gift of Paradise': ManaPermanent(name='Gift of Paradise', cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Glittering Frost': ManaPermanent(name='Glittering Frost', cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Market Festival':  ManaPermanent(name='Market Festival',  cmc=4, input_cost=0, payoff=1, enters_tapped=True),
    'Overgrowth':       ManaPermanent(name='Overgrowth',       cmc=3, input_cost=0, payoff=2, enters_tapped=True),
    'Sheltered Aerie':  ManaPermanent(name='Sheltered Aerie',  cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Utopia Sprawl':    ManaPermanent(name='Utopia Sprawl',    cmc=1, input_cost=0, payoff=1, enters_tapped=True),
    'Weirding Wood':    ManaPermanent(name='Weirding Wood',    cmc=3, input_cost=0, payoff=1, enters_tapped=True),
    'Wild Growth':      ManaPermanent(name='Wild Growth',      cmc=1, input_cost=0, payoff=1, enters_tapped=True),
    'Wolfwillow Haven': ManaPermanent(name='Wolfwillow Haven', cmc=2, input_cost=0, payoff=1, enters_tapped=True),

    # PLANESWALKERS
    'Domri, Anarch of Bolas': ManaPermanent(name='Domri, Anarch of Bolas', cmc=3, input_cost=0, payoff=1, enters_tapped=False),
    'Domri, Chaos Bringer':   ManaPermanent(name='Domri, Chaos Bringer',   cmc=4, input_cost=0, payoff=1, enters_tapped=False),

    # LAND FETCHERS
    # 1 CMC
    'Tithe': LandFetcher(name='Tithe', cmc=1, num_lands_to_hand=1),

    # 2 CMC
    'Farseek':        LandFetcher(name='Farseek',        cmc=2, num_tapped_lands_to_play=1),
    'Into the North': LandFetcher(name='Into the North', cmc=2, num_tapped_lands_to_play=1),
    'Rampant Growth': LandFetcher(name='Rampant Growth', cmc=2, num_tapped_lands_to_play=1),
    'Nature\'s Lore': LandFetcher(name='Nature\'s Lore', cmc=2, num_lands_to_play=1),
    'Three Visits':   LandFetcher(name='Three Visits',   cmc=2, num_lands_to_play=1),

    # 3 CMC
    'Cultivate':           LandFetcher(name='Cultivate',           cmc=3, num_tapped_lands_to_play=1, num_lands_to_hand=1),
    'Kodama\'s Reach':     LandFetcher(name='Kodama\'s Reach',     cmc=3, num_tapped_lands_to_play=1, num_lands_to_hand=1),
    'Far Wanderings':      LandFetcher(name='Far Wanderings',      cmc=3, num_tapped_lands_to_play=1),
    'Growth Spasm':        LandFetcher(name='Growth Spasm',        cmc=3, num_tapped_lands_to_play=1),
    'Harrow':              LandFetcher(name='Harrow',              cmc=3, num_lands_to_play=2, num_lands_to_sac=1),
    'Primal Growth':       LandFetcher(name='Primal Growth',       cmc=3, num_lands_to_play=1),
    'Recross the Paths':   LandFetcher(name='Recross the Paths',   cmc=3, num_lands_to_play=1),
    'Search for Tomorrow': LandFetcher(name='Search for Tomorrow', cmc=3, num_lands_to_play=1),
    'Spoils of Victory':   LandFetcher(name='Spoils of Victory',   cmc=3, num_lands_to_play=1),
    'Wood Elves':          LandFetcher(name='Wood Elves',          cmc=3, num_lands_to_play=1),

    # 4 CMC
    'Circuitous Route':     LandFetcher(name='Circuitous Route',     cmc=4, num_tapped_lands_to_play=2),
    'Reap and Sow':         LandFetcher(name='Reap and Sow',         cmc=4, num_lands_to_play=1),
    'Skyshroud Claim':      LandFetcher(name='Skyshroud Claim',      cmc=4, num_lands_to_play=2),
    'Solemn Simulacrum':    LandFetcher(name='Solemn Simulacrum',    cmc=4, num_tapped_lands_to_play=1),
    'Tempt with Discovery': LandFetcher(name='Tempt with Discovery', cmc=4, num_lands_to_play=1),

    # 5 CMC
    'Hour of Promise':  LandFetcher(name='Hour of Promise',  cmc=5, num_tapped_lands_to_play=2),

    # EXTRA LANDS
    'Azusa, Lost but Seeking':    ExtraLands(name='Azusa, Lost but Seeking',    cmc=3, num_extra_lands=2),
    'Dryad of the Ilysian Grove': ExtraLands(name='Dryad of the Ilysian Grove', cmc=3, num_extra_lands=1),
    'Ghirapur Orrery':            ExtraLands(name='Ghirapur Orrery',            cmc=4, num_extra_lands=1),
    'Exploration':                ExtraLands(name='Exploration',                cmc=1, num_extra_lands=1),
    'Wayward Swordtooth':         ExtraLands(name='Wayward Swordtooth',         cmc=3, num_extra_lands=1),

    # SAC ARTIFACTS
    'Burnished Hart':     SacPermanent(name='Burnished Hart',     cmc=3, activation_cost=3, num_tapped_lands_to_play=2),
    'Expedition Map':     SacPermanent(name='Expedition Map',     cmc=1, activation_cost=2, num_lands_to_hand=1),
    'Sakura-Tribe Elder': SacPermanent(name='Sakura-Tribe Elder', cmc=2, activation_cost=0, num_tapped_lands_to_play=1),
    'Wayfarer\'s Bauble': SacPermanent(name='Wayfarer\'s Bauble', cmc=1, activation_cost=2, num_tapped_lands_to_play=1),
}
# yapf: enable
