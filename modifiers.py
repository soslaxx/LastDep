from typing import Optional
from dataclasses import dataclass
from enum import Enum
import random


class ModifierType(Enum):
    GOLDEN = "golden"
    REPETITION = "repetition"
    BATTERY = "battery"
    CHAIN = "chain"
    TICKET = "ticket"
    TOKEN = "token"


@dataclass
class Modifier:
    type: ModifierType
    value: float = 1.0

    def apply(self, base_value: int) -> int:
        if self.type == ModifierType.GOLDEN:
            return int(base_value * (1.0 + self.value))
        return base_value


class Mods:
    def __init__(self):
        self.base_chc = {
            ModifierType.GOLDEN: 0.05,
            ModifierType.REPETITION: 0.03,
            ModifierType.BATTERY: 0.04,
            ModifierType.CHAIN: 0.03,
            ModifierType.TICKET: 0.06,
            ModifierType.TOKEN: 0.05,
        }
        self.ch_mult = {mod: 1.0 for mod in ModifierType}

    def roll(self, st: str) -> Optional[Modifier]:
        mods = []
        weights = []
        for mod_type, base_chc in self.base_chc.items():
            chance = base_chc * self.ch_mult[mod_type]
            if chance > 0:
                mods.append(mod_type)
                weights.append(chance)
        if not mods:
            return None
        twt = sum(weights)
        if twt <= 0:
            return None
        rnd = random.random() * twt
        acc = 0
        sel_mod = None
        for mod_type, weight in zip(mods, weights):
            acc += weight
            if rnd <= acc:
                sel_mod = mod_type
                break
        if not sel_mod:
            return None
        value = self._get_mod_val(sel_mod)
        return Modifier(type=sel_mod, value=value)

    def _get_mod_val(self, mod_type: ModifierType) -> float:
        values = {
            ModifierType.GOLDEN: 1.0,
            ModifierType.REPETITION: 1.0,
            ModifierType.BATTERY: 1.0,
            ModifierType.CHAIN: 1.5,
            ModifierType.TICKET: 1.0,
            ModifierType.TOKEN: 0.5,
        }
        return values.get(mod_type, 1.0)

    def set_ch_mult(self, mod_type: ModifierType, multiplier: float):
        self.ch_mult[mod_type] = multiplier

    def get_ch_mult(self, mod_type: ModifierType) -> float:
        return self.ch_mult.get(mod_type, 1.0)

    def reset_mults(self):
        self.ch_mult = {mod: 1.0 for mod in ModifierType}





