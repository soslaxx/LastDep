from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import random


class CharmTriggerType(Enum):
    RED_BUTTON = "red_button"
    RANDOM = "random"
    PASSIVE = "passive"
    ONE_TIME = "one_time"


@dataclass
class CharmEffect:
    type: str
    value: float = 1.0
    symbol: Optional[str] = None
    condition: Optional[str] = None


@dataclass
class Charm:
    id: str
    name: str
    desc: str
    cost: int
    trg_type: CharmTriggerType
    charges: int = 0
    max_chg: int = 0
    effects: List[CharmEffect] = field(default_factory=list)
    space_cost: int = 1
    rand_chc: float = 0.0
    unlock_cond: Optional[str] = None

    def can_go(self) -> bool:
        if self.trg_type == CharmTriggerType.RED_BUTTON:
            return self.charges > 0
        if self.trg_type == CharmTriggerType.RANDOM:
            return random.random() < self.rand_chc
        if self.trg_type == CharmTriggerType.PASSIVE:
            return True
        return False

    def use(self) -> bool:
        if not self.can_go():
            return False
        if self.trg_type == CharmTriggerType.RED_BUTTON:
            self.charges -= 1
        return True

    def fill(self, amount: int = 1):
        if self.trg_type == CharmTriggerType.RED_BUTTON:
            self.charges = min(self.max_chg, self.charges + amount)


CHARM_LIBRARY: Dict[str, Charm] = {}


def _register_charm(charm: Charm):
    CHARM_LIBRARY[charm.id] = charm


_register_charm(Charm(
    id="lucky_cat",
    name="Lucky Cat",
    desc="If 3+ Patterns trigger, earn coins equal to Interest",
    cost=3,
    trg_type=CharmTriggerType.PASSIVE,
    effects=[CharmEffect(type="interest_payout", value=1.0, condition="patterns_3+")],
))

_register_charm(Charm(
    id="chonky_cat",
    name="Chonky Cat",
    desc="If 7+ Patterns trigger, earn double Interest",
    cost=5,
    trg_type=CharmTriggerType.PASSIVE,
    effects=[CharmEffect(type="interest_payout", value=2.0, condition="patterns_7+")],
))

_register_charm(Charm(
    id="tarot_deck",
    name="Tarot Deck",
    desc="Symbols multiplier grows if charms trigger, resets if none trigger",
    cost=4,
    trg_type=CharmTriggerType.PASSIVE,
    effects=[CharmEffect(type="symbol_multiplier_growth", value=1.0)],
))

_register_charm(Charm(
    id="pentacle",
    name="Pentacle",
    desc="Symbols multiplier +1; grows by +1 when 5+ Patterns trigger",
    cost=4,
    trg_type=CharmTriggerType.PASSIVE,
    effects=[
        CharmEffect(type="symbol_multiplier", value=1.0),
        CharmEffect(type="symbol_multiplier_growth", value=1.0, condition="patterns_5+"),
    ],
))

_register_charm(Charm(
    id="red_shiny_rock",
    name="Red Shiny Rock",
    desc="Red Button: Grants Luck+4 next spin; consumes all charges",
    cost=4,
    trg_type=CharmTriggerType.RED_BUTTON,
    charges=2,
    max_chg=2,
    effects=[CharmEffect(type="luck_boost", value=4.0)],
))

_register_charm(Charm(
    id="ring_bell",
    name="Ring Bell",
    desc="Red Button: Increases all Symbols by base value permanently",
    cost=5,
    trg_type=CharmTriggerType.RED_BUTTON,
    charges=2,
    max_chg=2,
    effects=[CharmEffect(type="permanent_symbol_boost", value=1.0)],
))

_register_charm(Charm(
    id="midas_touch",
    name="Midas Touch",
    desc="Red Button: All scored Symbols increase permanently by base value",
    cost=7,
    trg_type=CharmTriggerType.RED_BUTTON,
    charges=1,
    max_chg=1,
    effects=[CharmEffect(type="permanent_symbol_boost", value=1.0)],
))

_register_charm(Charm(
    id="fake_coin",
    name="Fake Coin",
    desc="15% chance: grants +1 extra spin and Luck+4",
    cost=3,
    trg_type=CharmTriggerType.RANDOM,
    rand_chc=0.15,
    effects=[
        CharmEffect(type="extra_spin", value=1.0),
        CharmEffect(type="luck_boost", value=4.0),
    ],
))

_register_charm(Charm(
    id="property_certificate",
    name="Property Certificate",
    desc="Adds 2 extra Lucky Charm slots",
    cost=6,
    trg_type=CharmTriggerType.PASSIVE,
    space_cost=0,
    effects=[CharmEffect(type="charm_slots", value=2.0)],
))

_register_charm(Charm(
    id="car_battery",
    name="Car Battery",
    desc="Refills red charms slowly (doesn't take space)",
    cost=5,
    trg_type=CharmTriggerType.PASSIVE,
    space_cost=0,
    effects=[CharmEffect(type="red_charm_fill", value=1.0)],
))

_register_charm(Charm(
    id="nuclear_button",
    name="Nuclear Button",
    desc="Red Button variant: all red charms trigger once more, but -1 charm space",
    cost=7,
    trg_type=CharmTriggerType.PASSIVE,
    effects=[
        CharmEffect(type="red_button_repeat", value=1.0),
        CharmEffect(type="charm_slots", value=-1.0),
    ],
))

_register_charm(Charm(
    id="horseshoe",
    name="Horseshoe",
    desc="Charms with 'Triggers Randomly' activate more often (double frequency)",
    cost=4,
    trg_type=CharmTriggerType.PASSIVE,
    effects=[CharmEffect(type="random_charm_frequency", value=2.0)],
))

_register_charm(Charm(
    id="rotated_hamsa",
    name="Rotated Hamsa",
    desc="Grants Luck +7 for the last spin of a round",
    cost=3,
    trg_type=CharmTriggerType.PASSIVE,
    effects=[CharmEffect(type="luck_boost_last_spin", value=7.0)],
))

_register_charm(Charm(
    id="hamsa",
    name="Hamsa",
    desc="First spin of a round: +1 Pattern trigger",
    cost=4,
    trg_type=CharmTriggerType.PASSIVE,
    effects=[CharmEffect(type="extra_pattern_trigger", value=1.0, condition="first_spin")],
))

_register_charm(Charm(
    id="stocks",
    name="Stonks",
    desc="+5% to your Interest",
    cost=3,
    trg_type=CharmTriggerType.PASSIVE,
    effects=[CharmEffect(type="int_boost", value=5.0)],
))

_register_charm(Charm(
    id="cat_food",
    name="Cat Food",
    desc="+2 spins per round (stackable)",
    cost=4,
    trg_type=CharmTriggerType.PASSIVE,
    effects=[CharmEffect(type="extra_spins_per_round", value=2.0)],
))

_register_charm(Charm(
    id="bible",
    name="Holy Bible",
    desc="Blocks 666 events",
    cost=6,
    trg_type=CharmTriggerType.PASSIVE,
    effects=[CharmEffect(type="block_666", value=1.0)],
))

_register_charm(Charm(
    id="swole_cat",
    name="Swole Cat",
    desc="If 15+ Patterns trigger, earn 4× Interest",
    cost=8,
    trg_type=CharmTriggerType.PASSIVE,
    effects=[CharmEffect(type="interest_payout", value=4.0, condition="patterns_15+")],
))

_register_charm(Charm(
    id="grandmas_purse",
    name="Grandma's Purse",
    desc="+15% Interest; decreases by 3% every round; discarded when bonus reaches 0",
    cost=5,
    trg_type=CharmTriggerType.PASSIVE,
    effects=[CharmEffect(type="int_boost", value=15.0)],
))

_register_charm(Charm(
    id="one_trick_pony",
    name="One Trick Pony",
    desc="Grants 1 guaranteed jackpot next round, then discards",
    cost=7,
    trg_type=CharmTriggerType.ONE_TIME,
    effects=[CharmEffect(type="guaranteed_jackpot", value=1.0)],
))

_register_charm(Charm(
    id="super_capacitor",
    name="Super Capacitor",
    desc="After each spin, for every fully charged Red-Button charm, fill 1 energy to another random Red-Button charm",
    cost=6,
    trg_type=CharmTriggerType.PASSIVE,
    space_cost=0,
    effects=[CharmEffect(type="red_charm_fill", value=1.0)],
))

_register_charm(Charm(
    id="dynamo",
    name="Dynamo",
    desc="Triggers randomly at round end: chance to restore 1 charge to all bag Red-Button charms",
    cost=5,
    trg_type=CharmTriggerType.RANDOM,
    rand_chc=0.3,
    effects=[CharmEffect(type="red_charm_fill_all", value=1.0)],
))


class Charmm:
    def __init__(self, max_slots: int = 4):
        self.base_slots = max_slots
        self.max_slots = max_slots
        self.bag: List[Charm] = []
        self.ch_eff: Dict[str, float] = {}

    def can_add(self, charm: Charm) -> bool:
        used_slots = sum(c.space_cost for c in self.bag)
        av_slots = self.max_slots - used_slots
        return av_slots >= charm.space_cost

    def add(self, charm: Charm) -> bool:
        if not self.can_add(charm):
            return False
        clone_eff = [CharmEffect(type=e.type, value=e.value, symbol=e.symbol, condition=e.condition) for e in charm.effects]
        charm_copy = Charm(
            id=charm.id,
            name=charm.name,
            desc=charm.desc,
            cost=charm.cost,
            trg_type=charm.trg_type,
            charges=charm.max_chg,
            max_chg=charm.max_chg,
            effects=clone_eff,
            space_cost=charm.space_cost,
            rand_chc=charm.rand_chc,
        )
        self.bag.append(charm_copy)
        self._recalc()
        return True

    def drop(self, charm_id: str) -> bool:
        for i, charm in enumerate(self.bag):
            if charm.id == charm_id:
                self.bag.pop(i)
                self._recalc()
                return True
        return False

    def _recalc(self):
        self.ch_eff = {}
        self.max_slots = self.base_slots
        for charm in self.bag:
            for effect in charm.effects:
                if effect.type == "charm_slots":
                    self.max_slots = max(1, int(self.max_slots + effect.value))
                key = f"{effect.type}_{effect.symbol or ''}"
                if key in self.ch_eff:
                    self.ch_eff[key] += effect.value
                else:
                    self.ch_eff[key] = effect.value

    def _upd_cache(self):
        self._recalc()

    def val(self, effect_type: str, symbol: Optional[str] = None) -> float:
        key = f"{effect_type}_{symbol or ''}"
        return self.ch_eff.get(key, 0.0)

    def has(self, charm_id: str) -> bool:
        return any(c.id == charm_id for c in self.bag)

    def run_passive(self, condition: str, context: Dict) -> Dict:
        results = {
            "coins": 0,
            "tk": 0,
            "spin_left": 0,
            "luck": 0,
            "patterns": 0,
            "symbol_multiplier": 0.0,
            "pattern_multiplier": 0.0,
            "extra_pattern_triggers": 0,
            "luck_last_spin": 0,
        }
        pat_c = context.get("pat_c", 0)
        interest = context.get("interest", 0)

        for charm in self.bag:
            if charm.trg_type != CharmTriggerType.PASSIVE:
                continue
            for effect in charm.effects:
                if effect.condition:
                    if effect.condition.startswith("patterns_") and effect.condition.endswith("+"):
                        try:
                            required = int(effect.condition.split("_")[1].rstrip("+"))
                        except Exception:
                            required = 0
                        if pat_c < required:
                            continue
                    if effect.condition == "first_spin" and not condition.startswith("first_spin"):
                        continue
                if effect.type == "interest_payout":
                    results["coins"] += int(interest * effect.value)
                elif effect.type == "extra_spin":
                    results["spin_left"] += int(effect.value)
                elif effect.type == "luck_boost":
                    results["luck"] += int(effect.value)
                elif effect.type == "symbol_multiplier":
                    results["symbol_multiplier"] += effect.value
                elif effect.type == "pattern_multiplier":
                    results["pattern_multiplier"] += effect.value
                elif effect.type == "extra_pattern_trigger":
                    results["extra_pattern_triggers"] += int(effect.value)
                elif effect.type == "luck_boost_last_spin":
                    results["luck_last_spin"] += int(effect.value)
        return results

    def run_random(self) -> Dict:
        results = {
            "coins": 0,
            "tk": 0,
            "spin_left": 0,
            "luck": 0,
        }
        freq_bonus = self.val("random_charm_frequency")
        freq_mult = max(0.0, freq_bonus if freq_bonus > 0 else 1.0)
        for charm in self.bag:
            if charm.trg_type != CharmTriggerType.RANDOM:
                continue
            eff_chance = charm.rand_chc * freq_mult
            if random.random() < eff_chance:
                for effect in charm.effects:
                    if effect.type == "extra_spin":
                        results["spin_left"] += int(effect.value)
                    elif effect.type == "luck_boost":
                        results["luck"] += int(effect.value)
                    elif effect.type == "red_charm_fill_all":
                        self.fill_red(int(effect.value))
        return results

    def run_red(self) -> Dict:
        results = {
            "coins": 0,
            "tk": 0,
            "spin_left": 0,
            "luck": 0,
            "sym_boosts": {},
        }
        has_nuclear = any(c.id == "nuclear_button" for c in self.bag)
        rep_bonus = int(self.val("red_button_repeat"))
        rep_cnt = max(1, 1 + rep_bonus)
        if has_nuclear:
            rep_cnt += 1
        for _ in range(rep_cnt):
            for charm in self.bag:
                if charm.trg_type == CharmTriggerType.RED_BUTTON and charm.use():
                    for effect in charm.effects:
                        if effect.type == "luck_boost":
                            results["luck"] += int(effect.value)
                        elif effect.type == "permanent_symbol_boost":
                            results["sym_boosts"]["all"] = effect.value
        return results

    def use_once(self, effect_type: str) -> bool:
        for idx, charm in enumerate(self.bag):
            if charm.trg_type != CharmTriggerType.ONE_TIME:
                continue
            for effect in charm.effects:
                if effect.type == effect_type:
                    self.bag.pop(idx)
                    self._recalc()
                    return True
        return False

    def fill_red(self, amount: int = 1):
        bonus = int(self.val("red_charm_fill"))
        total = max(0, amount + bonus)
        for charm in self.bag:
            if charm.trg_type == CharmTriggerType.RED_BUTTON:
                charm.fill(total)

    def free_slots(self) -> int:
        used = sum(c.space_cost for c in self.bag)
        return max(0, self.max_slots - used)








