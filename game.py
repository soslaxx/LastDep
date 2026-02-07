import json
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import arcade
import arcade.gui as agui

from settings import load_config, save_config, TTF, btn_style
from savesystem import save_stats, load_best, load_stats
from patterns import Patt
from modifiers import Mods, Modifier, ModifierType
from charms import Charmm, CHARM_LIBRARY, CharmTriggerType

ROOT = Path("Data/assets")
IMG = ROOT / "images"
SFX = ROOT / "sfx"
SAVE = Path("Data/saves")
GAME_SAVE = SAVE / "game.json"

SYM = {
    "lemon": {"label": "LEMON", "value": 3, "weight": 194, "texture": "symbol_lemon.png", "color": (245, 230, 100)},
    "cherry": {"label": "CHERRY", "value": 3, "weight": 194, "texture": "symbol_cherry.png", "color": (230, 70, 90)},
    "clover": {"label": "CLOVER", "value": 5, "weight": 149, "texture": "symbol_clover.png", "color": (80, 190, 90)},
    "bell": {"label": "BELL", "value": 5, "weight": 149, "texture": "symbol_bell.png", "color": (235, 200, 40)},
    "diamond": {"label": "DIAMOND", "value": 8, "weight": 119, "texture": "symbol_diamond.png", "color": (80, 160, 230)},
    "treasure": {"label": "CHEST", "value": 8, "weight": 119, "texture": "symbol_treasure.png", "color": (150, 80, 200)},
    "seven": {"label": "777", "value": 12, "weight": 75, "texture": "symbol_seven.png", "color": (255, 130, 50)},
    "six": {"label": "666", "value": -80, "weight": 20, "texture": "symbol_six.png", "color": (200, 50, 50)},
    "ticket": {"label": "TICKET", "value": 0, "weight": 0, "texture": "symbol_ticket.png", "color": (200, 180, 120)},
}


@dataclass
class Cell:
    symbol: str
    mod: Optional[Modifier] = None
    sprite: Optional[arcade.Sprite] = None


class Slot(arcade.Window):
    def __init__(self):
        self.cfg = load_config()
        super().__init__(
            self.cfg["WWidth"],
            self.cfg["WHeight"],
            self.cfg["WTitle"],
            fullscreen=self.cfg["WFullScreen"],
        )
        try:
            self.set_fullscreen(self.cfg["WFullScreen"])
            if not self.cfg["WFullScreen"]:
                self.set_size(self.cfg["WWidth"], self.cfg["WHeight"])
        except Exception:
            pass
        arcade.load_font(TTF["CAUSE"])
        arcade.load_font(TTF["HYDRA"])
        arcade.load_font(TTF["QUICKSAND"])

        self.ui: Optional[agui.UIManager] = None
        self.st = "menu"

        self.pat = Patt(rows=3, cols=5)
        self.mods = Mods()
        self.charms = Charmm(max_slots=self.cfg["InitCharmSlots"])
        self.pay_boost = 3.2

        self.cells: List[List[Cell]] = []
        self.spr = arcade.SpriteList()
        self.box = arcade.LBWH(0, 0, 0, 0)
        self.spin_on = False
        self.spin_t = 0
        self.buf: Optional[Dict] = None

        self.cash = 0
        self.tk = 0
        self.spin_left = 0
        self.spin_round = 0
        self.rnds = 0
        self.dbt = 0
        self.lv = 1
        self.rt = 0

        self.sb: Dict[str, int] = {k: 0 for k in SYM.keys()}
        self.sm = 1.0
        self.static_sm = 0.0
        self.pm = 1.0
        self.lbuf = 0
        self.luck = 0
        self.ltemp = 0
        self.lt_sp_left = 0
        self.pay_boost = 3.2

        self.sixf = False

        self.tx: Dict[str, arcade.Texture] = {}
        self.snd: Dict[str, Optional[arcade.Sound]] = {}
        self.pt: List[Dict] = []
        self.shk = 0.0
        self.bg: Optional[arcade.Texture] = None
        self.stx: Optional[arcade.Texture] = None

        self.msg = ""
        self.last: Dict = {}
        self.fin: Optional[Dict] = None

        self.shop: List[str] = []
        self.shopr = 0

        self.cam = None
        self.ui_cam = None
        self.hl: List[List[tuple]] = []
        self.hi = 0
        self.ht = 0.0
        self.hlen = 1.4
        self.shop_on = False

        self.load_tx()
        self.load_sd()
        self.rst()
        self.menu()

        self.cam_sync()

    def save_game(self):
        try:
            SAVE.mkdir(parents=True, exist_ok=True)
            data = {
                "cash": self.cash,
                "tk": self.tk,
                "spin_left": self.spin_left,
                "spin_round": self.spin_round,
                "rnds": self.rnds,
                "dbt": self.dbt,
                "lv": self.lv,
                "rt": self.rt,
                "luck": self.luck,
                "ltemp": self.ltemp,
                "lt_sp_left": self.lt_sp_left,
                "sb": self.sb,
                "sm": self.sm,
                "static_sm": self.static_sm,
                "pm": self.pm,
                "lbuf": self.lbuf,
                "sixf": self.sixf,
                "shop": self.shop,
                "shopr": self.shopr,
                "cells": [[cell.symbol for cell in row] for row in self.cells],
                "mods": [
                    [
                        {"type": cell.mod.type.value, "value": cell.mod.value} if cell.mod else None
                        for cell in row
                    ]
                    for row in self.cells
                ],
                "charms": [
                    {"id": c.id, "charges": c.charges, "max_chg": c.max_chg}
                    for c in self.charms.bag
                ],
                "mods_mult": {mt.name: val for mt, val in self.mods.ch_mult.items()},
                "last": self.last,
                "msg": self.msg,
            }
            GAME_SAVE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            pass

    def load_game(self) -> bool:
        if not GAME_SAVE.exists():
            return False
        try:
            data = json.loads(GAME_SAVE.read_text(encoding="utf-8"))
        except Exception:
            return False

        self.rst()

        self.cash = data.get("cash", self.cash)
        self.tk = data.get("tk", self.tk)
        self.spin_left = data.get("spin_left", self.spin_left)
        self.spin_round = data.get("spin_round", self.spin_round)
        self.rnds = data.get("rnds", self.rnds)
        self.dbt = data.get("dbt", self.dbt)
        self.lv = data.get("lv", self.lv)
        self.rt = data.get("rt", self.rt)
        self.luck = data.get("luck", self.luck)
        self.ltemp = data.get("ltemp", self.ltemp)
        self.lt_sp_left = data.get("lt_sp_left", self.lt_sp_left)
        self.sb = data.get("sb", self.sb)
        self.sm = data.get("sm", self.sm)
        self.static_sm = data.get("static_sm", self.static_sm)
        self.pm = data.get("pm", self.pm)
        self.lbuf = data.get("lbuf", self.lbuf)
        self.sixf = data.get("sixf", self.sixf)
        self.shop = data.get("shop", self.shop_roll())
        self.shopr = data.get("shopr", 0)
        self.last = data.get("last", {})
        self.msg = data.get("msg", "")

        self.charms.bag = []
        for cdata in data.get("charms", []):
            cid = cdata.get("id")
            if cid in CHARM_LIBRARY:
                base = CHARM_LIBRARY[cid]
                self.charms.add(base)
                self.charms.bag[-1].charges = cdata.get("charges", base.max_chg)
                self.charms.bag[-1].max_chg = cdata.get("max_chg", base.max_chg)
        self.charms._recalc()

        for mt_name, val in data.get("mods_mult", {}).items():
            try:
                mt = ModifierType[mt_name]
                self.mods.ch_mult[mt] = val
            except Exception:
                continue

        self.grid_build()
        saved_cells = data.get("cells")
        saved_mods = data.get("mods")
        if saved_cells:
            for r, row in enumerate(self.cells):
                for c, cell in enumerate(row):
                    try:
                        sym = saved_cells[r][c]
                        cell.symbol = sym
                        if cell.sprite:
                            cell.sprite.texture = self.tx.get(sym, cell.sprite.texture)
                    except Exception:
                        continue
        if saved_mods:
            for r, row in enumerate(self.cells):
                for c, cell in enumerate(row):
                    try:
                        md = saved_mods[r][c]
                        if md:
                            mtype = ModifierType(md["type"])
                            cell.mod = Modifier(type=mtype, value=md["value"])
                        else:
                            cell.mod = None
                    except Exception:
                        cell.mod = None

        return True
    def _ui_style(self, font_size: int = 24):
        return {
            "normal": agui.UIFlatButton.UIStyle(
                font_size=font_size,
                font_name="CAUSE",
                bg=arcade.color.TRANSPARENT_BLACK,
                border=None,
            ),
            "hover": agui.UIFlatButton.UIStyle(
                font_size=font_size,
                font_name="CAUSE",
                font_color=arcade.color.YELLOW,
                bg=arcade.color.TRANSPARENT_BLACK,
                border=None,
            ),
            "press": agui.UIFlatButton.UIStyle(
                font_size=font_size,
                font_name="CAUSE",
                font_color=arcade.color.ORANGE,
                bg=arcade.color.TRANSPARENT_BLACK,
                border=None,
            ),
        }

    def load_tx(self):
        for key, data in SYM.items():
            tex_path = IMG / data["texture"]
            if tex_path.exists():
                self.tx[key] = arcade.load_texture(tex_path)
            else:
                texture = arcade.make_soft_square_texture(104, data["color"], outer_alpha=240)
                self.tx[key] = texture

        bg_path = IMG / "room.png"
        self.bg = arcade.load_texture(bg_path) if bg_path.exists() else None
        slot_path = IMG / "slot_body.png"
        self.stx = arcade.load_texture(slot_path) if slot_path.exists() else None

    def load_sd(self):
        for name in ["spin", "win", "button", "lose", "shop"]:
            path = SFX / f"{name}.wav"
            if path.exists():
                try:
                    self.snd[name] = arcade.load_sound(path)
                except Exception:
                    self.snd[name] = None
    def play_snd(self, name: str):
        snd = self.snd.get(name)
        if snd:
            try:
                snd.play(volume=0.35)
            except Exception:
                pass

    def rst(self):
        self.cfg = load_config()
        self.cash = self.cfg["InitSatoshi"]
        self.tk = self.cfg["InitTickets"]
        self.spin_round = self.cfg["Initspin_left"]
        self.spin_left = self.spin_round
        self.rnds = self.cfg["Initrnds"]
        self.lv = 1
        self.dbt = self.cfg["InitDebt"]
        self.rt = self.cfg["InitInterest"]
        self.luck = self.cfg["InitLuck"]
        self.ltemp = 0
        self.lt_sp_left = 0

        self.sb = {k: 0 for k in SYM.keys()}
        self.sm = self.cfg["InitMultiply"]
        self.static_sm = 0.0
        self.pm = self.cfg["InitMultiply"]
        self.lbuf = 0
        self.sixf = False

        self.charms = Charmm(max_slots=self.cfg["InitCharmSlots"])
        self.mods.reset_mults()

        self.rt_upd()
        self.mult_sync()

        self.shop = self.shop_roll()

        self.grid_build()

        self.msg = ""
        self.last = {}
        self.fin = None
        self.spin_on = False
        self.buf = None
        self.hl = []
        self.hi = 0
        self.ht = 0.0
        self.shopr = 0
        self.shop_on = False

    def shop_roll(self) -> List[str]:
        pool = list(CHARM_LIBRARY.keys())
        random.shuffle(pool)
        return pool[:6]

    def shop_cost(self) -> int:
        return max(10, 40 + (self.lv - 1) * 15 + self.shopr * 8)

    def grid_build(self):
        self.cam_sync()

        self.spr = arcade.SpriteList()
        self.cells = []
        size = 104
        padding = 8
        total_w = 5 * size + 4 * padding
        total_h = 3 * size + 2 * padding

        win_width = self.width
        win_height = self.height

        left = (win_width - total_w) // 2
        bottom = (win_height - total_h) // 2
        self.box = arcade.LBWH(left - 20, bottom - 20, total_w + 40, total_h + 40)

        tex_sample = next(iter(self.tx.values()))
        if tex_sample.width:
            self.symbol_scale = size / tex_sample.width
        else:
            self.symbol_scale = 1

        for row in range(3):
            row_cells = []
            for col in range(5):
                symbol = random.choice(list(SYM.keys()))
                sprite = arcade.Sprite(
                    self.tx[symbol],
                    center_x=left + col * (size + padding) + size // 2,
                    center_y=bottom + (2 - row) * (size + padding) + size // 2,
                    scale=self.symbol_scale,
                )
                self.spr.append(sprite)
                row_cells.append(Cell(symbol=symbol, sprite=sprite))
            self.cells.append(row_cells)

    def wt(self, symbol: str, luck_value: Optional[float] = None) -> float:
        bw = SYM[symbol]["weight"]
        if symbol == "ticket":
            return 0
        luck = (self.luck + self.ltemp) if luck_value is None else luck_value
        value = SYM[symbol]["value"]

        if symbol == "six":
            bw = max(1, bw - luck * 0.4)
        else:
            if value >= 8:
                bw = max(1, bw * (1.0 + luck * 0.06))
            elif value >= 5:
                bw = max(1, bw * (1.0 + luck * 0.04))
            else:
                bw = max(1, bw * (1.0 - luck * 0.03))
        return bw

    def spin_prep(self) -> Dict:
        cells: List[List[str]] = []
        mod_grid: List[List[Optional[Modifier]]] = []

        spin_luck = self.luck + self.lbuf
        spin_luck += self.ltemp
        if self.spin_left == 0:
            spin_luck += int(self.charms.val("luck_boost_last"))
        force_jp = self.charms.use_once("guaranteed_jackpot")

        if force_jp:
            choices = [k for k in SYM.keys() if k not in ("six", "ticket")]
            symbol_choice = random.choice(choices) if choices else "seven"
            cells = [[symbol_choice for _ in range(5)] for _ in range(3)]
            mod_grid = [[None for _ in range(5)] for _ in range(3)]
        else:
            for _ in range(3):
                grid_row = []
                mod_row = []
                for _col in range(5):
                    symbols = list(SYM.keys())
                    weights = [self.wt(s, luck_value=spin_luck) for s in symbols]
                    symbol = random.choices(symbols, weights=weights, k=1)[0]
                    grid_row.append(symbol)
                    mod = self.mods.roll(symbol)
                    mod_row.append(mod)
                cells.append(grid_row)
                mod_grid.append(mod_row)

        six_c = sum(1 for row in cells for sym in row if sym == "six")
        six_six_six = six_c >= 3

        pat_m = self.pat.find_all(cells)

        tot_coins = 0
        tot_tk = 0
        pat_c = len(pat_m)

        for match in pat_m:
            st = match.sym_type
            base_value = SYM[st]["value"]
            sv = base_value + self.sb.get(st, 0)

            for row, col in match.symbols:
                mod = mod_grid[row][col]
                if mod:
                    if mod.type == ModifierType.GOLDEN:
                        sv = mod.apply(sv)
                    elif mod.type == ModifierType.TOKEN:
                        tot_coins += int(self.rt * mod.value)

            pat_val = sv * match.length * match.base_val * self.pay_boost
            pat_val *= self.pm
            pat_val *= self.sm
            tot_coins += int(pat_val)

        int_bonus = int(tot_coins * (self.rt / 100))
        tot_coins += int_bonus

        if six_six_six:
            has_bible = self.charms.has("bible")
            if not has_bible:
                tot_coins = min(0, tot_coins - abs(SYM["six"]["value"]) * 3)
                self.luck = max(0, self.luck - 5)
                self.sixf = True

        return {
            "cells": cells,
            "modifiers": mod_grid,
            "patterns": pat_m,
            "pat_c": pat_c,
            "coins": max(0, tot_coins),
            "tk": tot_tk,
            "six_six_six": six_six_six,
            "jackpot": any(m.pat_type == "JACKPOT" for m in pat_m),
        }

    def spin_end(self):
        if not self.buf:
            return

        result = self.buf

        for row_idx, row in enumerate(result["cells"]):
            for col_idx, symbol in enumerate(row):
                cell = self.cells[row_idx][col_idx]
                cell.symbol = symbol
                cell.mod = result["modifiers"][row_idx][col_idx]
                if cell.sprite:
                    cell.sprite.texture = self.tx[symbol]
        self.hl = [match.symbols for match in result["patterns"]]
        self.hi = 0
        self.ht = 0.0

        if result["six_six_six"] and not self.charms.has("bible"):
            self.st = "final"
            self.fin = {
                "lv": self.lv,
                "cash": self.cash,
                "dbt": self.dbt,
                "tk": self.tk,
                "rt": self.rt,
            }
            self.msg = "666! Ты проиграл."
            self.run_save()
            self.fin_build()
            self.play_snd("lose")
            self.buf = None
            self.spin_on = False
            return

        coin_gain = result["coins"]
        t_e = result["tk"]
        pat_c = result["pat_c"]
        base_coin = coin_gain
        if pat_c > 0:
            coin_gain = int(coin_gain * 1.5) + 10

        cond_str = f"patterns_{pat_c}"
        if self.spin_left == self.spin_round - 1:
            cond_str = "first_spin"

        pass_r = self.charms.run_passive(
            cond_str,
            {"rt": self.rt, "pat_c": pat_c},
        )
        coin_gain += pass_r["coins"]
        t_e += pass_r["tk"]
        self.spin_left += pass_r["spin_left"]
        if pass_r.get("luck", 0):
            self.ltemp += pass_r["luck"]
            self.lt_sp_left = max(self.lt_sp_left, 2)
        if pass_r.get("symbol_multiplier", 0):
            self.sm += pass_r["symbol_multiplier"]
        if pass_r.get("pattern_multiplier", 0):
            self.pm += pass_r["pattern_multiplier"]
        if pass_r.get("extra_pattern_triggers", 0):
            coin_gain += int(base_coin * pass_r["extra_pattern_triggers"])

        rand_r = self.charms.run_random()
        coin_gain += rand_r["coins"]
        t_e += rand_r["tk"]
        self.spin_left += rand_r["spin_left"]
        if rand_r["luck"] > 0:
            self.ltemp += rand_r["luck"]
            self.lt_sp_left = max(self.lt_sp_left, 2)

        if self.lbuf:
            self.ltemp += self.lbuf
            self.lt_sp_left = max(self.lt_sp_left, 2)
            self.lbuf = 0

        has_tarot = self.charms.has("tarot_deck")
        if has_tarot:
            if pat_c > 0 or pass_r["coins"] > 0 or rand_r["coins"] > 0:
                self.sm += 0.5
            else:
                self.sm = max(1.0, self.sm - 0.5)

        if pat_c >= 5:
            has_pentacle = self.charms.has("pentacle")
            if has_pentacle:
                self.sm += 1.0

        self.cash += coin_gain
        self.tk += t_e

        if self.spin_left <= 0:
            self.charms.fill_red(1)

        self.last = {
            "coins": coin_gain,
            "tk": t_e,
            "patterns": pat_c,
            "six_six_six": result["six_six_six"],
            "jackpot": result["jackpot"],
        }

        self.msg = f"+{coin_gain} coins, +{t_e} tickets, {pat_c} patterns"

        if result["jackpot"]:
            self.shk = 0.3 if self.cfg["Enableshk"] else 0
            self.pt_spawn(center=True)
            self.play_snd("win")
        elif pat_c > 0:
            if self.cfg["Enablept"]:
                self.pt_spawn()
            self.play_snd("win")

        self.buf = None
        self.spin_on = False

        if self.spin_left <= 0:
            self.dead_end()
        else:
            self.save_game()

    def spin_go(self):
        if self.st != "game":
            return
        if self.shop_on:
            return
        if self.spin_on or self.spin_left <= 0:
            return

        self.hl = []
        self.hi = 0
        self.ht = 0.0

        self.spin_left -= 1
        self.play_snd("spin")

        self.buf = self.spin_prep()
        self.spin_t = time.time() + 2.4
        self.spin_on = True
        self.save_game()

    def red_go(self):
        if self.st != "game":
            return
        if self.shop_on:
            return

        results = self.charms.run_red()

        if results["luck"] > 0:
            self.lbuf += results["luck"]

        if results["sym_boosts"]:
            for symbol in self.sb:
                base_value = SYM[symbol]["value"]
                self.sb[symbol] += int(base_value * results["sym_boosts"].get("all", 0))

        if results["luck"] > 0 or results["sym_boosts"]:
            self.play_snd("button")
            self.msg = "Red Button activated!"
        else:
            self.msg = "No red charms ready"
        self.charms.bag = [c for c in self.charms.bag if not (c.trg_type == CharmTriggerType.RED_BUTTON and c.charges <= 0)]
        self.charms._upd_cache()

    def dead_end(self):
        if self.cash >= self.dbt:
            unused_sp = max(0, self.spin_left)
            if unused_sp > 0:
                self.tk += unused_sp
            self.cash -= self.dbt
            paid = self.dbt

            self.lv += 1
            debt_table = {
                1: 200,
                2: 666,
                3: 2222,
                4: 12500,
                5: 33333,
                6: 66666,
                7: 300000,
                8: 1000000,
                9: 6000000,
            }
            if self.lv in debt_table:
                self.dbt = debt_table[self.lv]
            else:
                self.dbt = int(self.dbt * 3.0)
            base_sp = self.cfg["Initspin_left"] + self.lv // 2

            extra_sp = int(self.charms.val("extra_sp_round"))
            self.spin_round = base_sp + extra_sp
            self.spin_left = self.spin_round
            self.rnds = max(1, self.rnds - 1)

            self.charms.fill_red(1)
            self.shopr = 0
            self.shop = self.shop_roll()
            purse_dim = False
            for charm in list(self.charms.bag):
                if charm.id == "grandmas_purse":
                    for effect in charm.effects:
                        if effect.type == "int_boost":
                            effect.value = max(0, effect.value - 3)
                    if all(e.type == "int_boost" and e.value <= 0 for e in charm.effects):
                        self.charms.unadd(charm.id)
                        purse_dim = True
            self.rt_upd()
            self.mult_sync()

            bonus_msg = f" +{unused_sp} tickets for early payoff" if unused_sp > 0 else ""
            purse_msg = " Grandma's Purse faded." if purse_dim else ""
            self.msg = f"Debt cleared! Paid {paid}. Next deadline: {self.dbt}{bonus_msg}{purse_msg}"
            self.play_snd("win")
        else:
            self.st = "final"
            self.fin = {
                "lv": self.lv,
                "cash": self.cash,
                "dbt": self.dbt,
                "tk": self.tk,
                "rt": self.rt,
            }
            self.run_save()
            self.fin_build()
            self.play_snd("lose")

    def run_save(self):
        SAVE.mkdir(parents=True, exist_ok=True)
        path = SAVE / "runs.csv"
        line = f"{int(time.time())};{self.lv};{self.cash};{self.dbt};{self.tk};{self.rt}\n"
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception:
            pass
        max_pat_coins = self.last.get("coins", 0) if self.last else 0
        save_stats(
            {
                "runs": 1,
                "spins": self.cfg["Initrnds"] * self.cfg["Initspin_left"],
                "coins": self.cash,
                "tickets": self.tk,
                "balance": self.cash,
                "level": self.lv,
                "max_pat_coins": max_pat_coins,
            }
        )

    def charm_buy(self, charm_id: str):
        if charm_id not in CHARM_LIBRARY:
            self.msg = "Charm not found"
            return

        charm = CHARM_LIBRARY[charm_id]

        if self.tk < charm.cost:
            self.msg = "Not enough tickets"
            return

        if not self.charms.can_add(charm):
            self.msg = "No charm slots available"
            return

        if any(c.id == charm_id for c in self.charms.bag):
            self.msg = "Already have"
            return

        self.tk -= charm.cost
        self.charms.add(charm)

        self.mult_sync()
        self.rt_upd()

        self.msg = f"Bought {charm.name}"
        self.play_snd("shop")
        self.shop = self.shop_roll()
        self.shop_on = False
        self.game_build()

    def pt_spawn(self, center: bool = False):
        if not self.cfg["Enablept"]:
            return

        if center:
            cx, cy = self.width // 2, self.height // 2
        else:
            if self.cells:
                middle = self.cells[1][2]
                if middle.sprite:
                    cx, cy = middle.sprite.center_x, middle.sprite.center_y
                else:
                    cx, cy = self.width // 2, self.height // 2
            else:
                cx, cy = self.width // 2, self.height // 2

        for _ in range(25):
            self.pt.append(
                {
                    "x": cx + random.randint(-40, 40),
                    "y": cy + random.randint(-20, 60),
                    "dx": random.uniform(-1.4, 1.4),
                    "dy": random.uniform(1.0, 2.4),
                    "life": random.uniform(0.4, 0.9),
                    "size": random.randint(4, 9),
                    "color": random.choice([(255, 215, 0), (255, 150, 50), (200, 255, 180)]),
                }
            )

    def update_pt(self, delta_time: float):
        new_list = []
        for p in self.pt:
            p["life"] -= delta_time
            if p["life"] <= 0:
                continue
            p["x"] += p["dx"] * 60 * delta_time
            p["y"] += p["dy"] * 60 * delta_time
            p["dy"] -= 0.02
            new_list.append(p)
        self.pt = new_list

    def menu(self):
        self.shop_on = False
        if self.ui:
            self.ui.disable()
        self.ui = agui.UIManager(self)
        self.ui.enable()
        layout = agui.UILayout(x=0, y=0, width=self.width, height=self.height)

        center_x = self.width // 2
        center_y = self.height // 2

        title = agui.UILabel(
            text="LASTDEP",
            x=center_x - 300 // 2,
            y=center_y + 120,
            width=350,
            height=80,
            text_color=(255, 200, 0),
            font_size=60,
            font_name="HYDRA",
            align="center",
            bold=True,
        )

        play_btn = agui.UIFlatButton(
            text="[♣] ENTER",
            x=center_x - 390 // 2,
            y=center_y,
            width=300,
            height=50,
            style=btn_style,
        )
        stats_btn = agui.UIFlatButton(
            text="[♠] STATS",
            x=center_x - 300 // 2,
            y=center_y - 60,
            width=240,
            height=50,
            style=btn_style,
        )
        set_btn = agui.UIFlatButton(
            text="[♦] SETTINGS",
            x=center_x - 340 // 2,
            y=center_y - 120,
            width=300,
            height=50,
            style=btn_style,
        )
        exit_btn = agui.UIFlatButton(
            text="[♥] EXIT",
            x=center_x - 320 // 2,
            y=center_y - 180,
            width=300,
            height=50,
            style=btn_style,
        )

        @play_btn.event("on_click")
        def _(_event):
            if GAME_SAVE.exists():
                dialog = agui.UIMessageBox(
                    width=420,
                    height=220,
                    message_text="Continue saved game?",
                    buttons=["Continue", "New"],
                )

                @dialog.event("on_action")
                def on_action(event):
                    try:
                        dialog.parent.remove(dialog)
                    except Exception:
                        pass
                    choice = event.action
                    if choice == "Continue" and self.load_game():
                        self.st = "game"
                        self.cam_sync()
                        self.game_build()
                    else:
                        if GAME_SAVE.exists():
                            try:
                                GAME_SAVE.unlink()
                            except Exception:
                                pass
                        self.rst()
                        self.st = "game"
                        self.cam_sync()
                        self.grid_build()
                        self.game_build()

                self.ui.add(dialog)
            else:
                self.rst()
                self.st = "game"
                self.cam_sync()
                self.grid_build()
                self.game_build()

        @set_btn.event("on_click")
        def _(_event):
            self.st = "cfg"
            self.set_build()

        @stats_btn.event("on_click")
        def _(_event):
            self.stats_show()

        @exit_btn.event("on_click")
        def _(_event):
            arcade.close_window()

        layout.add(title)
        layout.add(play_btn)
        layout.add(stats_btn)
        layout.add(set_btn)
        layout.add(exit_btn)
        self.ui.add(layout)
        self.st = "menu"

    def stats_show(self):
        stats = load_stats()
        if self.ui:
            self.ui.disable()
        self.ui = agui.UIManager(self)
        self.ui.enable()

        rows = [
            ("Total runs", stats.get("tot_runs", 0)),
            ("Total spins", stats.get("tot_spins", 0)),
            ("Total coins", stats.get("tot_coins", 0)),
            ("Total tickets", stats.get("tot_tk", 0)),
            ("Best balance", stats.get("best_bal", 0)),
            ("Best level", stats.get("best_lvl", 0)),
            ("Max combo payout", stats.get("best_pat_win", 0)),
        ]

        layout = agui.UIBoxLayout(vertical=True, space_between=10)
        title = agui.UILabel(text="Statistics", font_name="HYDRA", font_size=28, text_color=(255, 210, 60))
        layout.add(title)

        for label_txt, value in rows:
            row = agui.UIBoxLayout(vertical=False, space_between=12)
            row.add(
                agui.UILabel(
                    text=label_txt,
                    font_name="CAUSE",
                    font_size=20,
                    text_color=(235, 235, 235),
                    width=240,
                )
            )
            row.add(
                agui.UILabel(
                    text=str(value),
                    font_name="QUICKSAND",
                    font_size=20,
                    text_color=(200, 220, 255),
                    width=200,
                )
            )
            layout.add(row)

        close_btn = agui.UIFlatButton(text="CLOSE", width=220, height=52, style=btn_style)

        @close_btn.event("on_click")
        def _(_event):
            self.menu()

        layout.add(close_btn)
        anchor = agui.UIAnchorLayout()
        anchor.add(child=layout, anchor_x="center", anchor_y="center")
        self.ui.add(anchor)

    def set_build(self):
        if self.ui:
            self.ui.disable()
        self.ui = agui.UIManager(self)
        self.ui.enable()
        buffer = self.cfg.copy()

        layout = agui.UIBoxLayout(vertical=True, space_between=12)
        title = agui.UILabel(text="Settings", font_name="HYDRA", font_size=40, text_color=(255, 210, 60))
        layout.add(title)

        def small_style():
            return {
                "normal": agui.UIFlatButton.UIStyle(font_size=20, font_name="CAUSE", bg=arcade.color.TRANSPARENT_BLACK, border=None),
                "hover": agui.UIFlatButton.UIStyle(font_size=20, font_name="CAUSE", font_color=arcade.color.YELLOW, bg=arcade.color.TRANSPARENT_BLACK, border=None),
                "press": agui.UIFlatButton.UIStyle(font_size=20, font_name="CAUSE", font_color=arcade.color.ORANGE, bg=arcade.color.TRANSPARENT_BLACK, border=None),
            }

        def num_row(label, key, step, minimum, maximum):
            row = agui.UIBoxLayout(vertical=False, space_between=8)
            text_label = agui.UILabel(text=f"{label}: {buffer[key]}", font_name="CAUSE", font_size=20, text_color=(220, 220, 220))

            def refresh():
                text_label.text = f"{label}: {buffer[key]}"

            minus_btn = agui.UIFlatButton(text="-", width=40, height=40, style=small_style())
            plus_btn = agui.UIFlatButton(text="+", width=40, height=40, style=small_style())

            @minus_btn.event("on_click")
            def _(_event):
                buffer[key] = max(minimum, buffer[key] - step)
                refresh()

            @plus_btn.event("on_click")
            def _(_event):
                buffer[key] = min(maximum, buffer[key] + step)
                refresh()

            row.add(text_label)
            row.add(minus_btn)
            row.add(plus_btn)
            layout.add(row)

        def toggle_row(label, key):
            btn = agui.UIFlatButton(text=f"{label}: {buffer[key]}", width=260, height=40, style=small_style())

            @btn.event("on_click")
            def _(_event):
                buffer[key] = not buffer[key]
                btn.text = f"{label}: {buffer[key]}"

            layout.add(btn)

        num_row("Width", "WWidth", 80, 960, 1920)
        num_row("Height", "WHeight", 60, 600, 1200)
        toggle_row("Fullscreen", "WFullScreen")
        num_row("Coins start", "InitSatoshi", 10, 20, 500)
        num_row("Spins per round", "Initspin_left", 1, 3, 20)
        num_row("Rounds", "Initrnds", 1, 1, 10)
        num_row("Debt base", "InitDebt", 10, 60, 2000)
        num_row("Tickets start", "InitTickets", 1, 0, 30)
        num_row("Interest %", "InitInterest", 1, 0, 50)
        num_row("Charm slots", "InitCharmSlots", 1, 2, 10)
        num_row("Base luck", "InitLuck", 1, 0, 50)
        toggle_row("Particles", "Enablept")
        toggle_row("Screen shake", "Enableshk")

        btn_row = agui.UIBoxLayout(vertical=False, space_between=10)
        back_btn = agui.UIFlatButton(text="Back", width=200, height=50, style=btn_style)
        save_btn = agui.UIFlatButton(text="Save", width=200, height=50, style=btn_style)

        @back_btn.event("on_click")
        def _(_event):
            self.menu()

        @save_btn.event("on_click")
        def _(_event):
            save_config(buffer)
            self.cfg = buffer.copy()
            if self.cfg["WFullScreen"]:
                self.set_fullscreen(True)
            else:
                self.set_fullscreen(False)
                self.set_size(self.cfg["WWidth"], self.cfg["WHeight"])
            self.menu()

        btn_row.add(back_btn)
        btn_row.add(save_btn)
        layout.add(btn_row)
        anchor = agui.UIAnchorLayout()
        anchor.add(child=layout, anchor_x="center", anchor_y="center")
        self.ui.add(anchor)

    def game_build(self):
        if self.ui:
            self.ui.disable()
        self.ui = agui.UIManager(self)
        self.ui.enable()
        self.shop_on = False
        style = self._ui_style(font_size=24)
        layout = agui.UIBoxLayout(vertical=False, space_between=32)

        spin_btn = agui.UIFlatButton(text=f"SPIN ({self.spin_left})", width=260, height=64, style=style)
        red_btn = agui.UIFlatButton(text="RED BUTTON (R)", width=260, height=64, style=style)
        shop_btn = agui.UIFlatButton(text="SHOP", width=180, height=64, style=style)
        dep_btn = agui.UIFlatButton(text="DEPOSIT", width=180, height=64, style=style)
        set_btn = agui.UIFlatButton(text="SETTINGS", width=200, height=64, style=style)
        quit_btn = agui.UIFlatButton(text="MENU", width=160, height=64, style=style)

        @spin_btn.event("on_click")
        def _(_event):
            self.spin_go()
            spin_btn.text = f"SPIN ({self.spin_left})"

        @red_btn.event("on_click")
        def _(_event):
            self.red_go()

        @shop_btn.event("on_click")
        def _(_event):
            self.shop_show()

        @dep_btn.event("on_click")
        def _(_event):
            if self.st == "game" and self.cash >= self.dbt:
                self.dead_end()

        @set_btn.event("on_click")
        def _(_event):
            self.st = "cfg"
            self.set_build()

        @quit_btn.event("on_click")
        def _(_event):
            self.st = "menu"
            self.menu()

        layout.add(spin_btn)
        layout.add(red_btn)
        layout.add(shop_btn)
        layout.add(dep_btn)
        layout.add(set_btn)
        layout.add(quit_btn)

        anchor = agui.UIAnchorLayout()
        anchor.add(child=layout, anchor_x="center", anchor_y="bottom", align_y=26)
        self.ui.add(anchor)

    def shop_show(self):
        style = self._ui_style(font_size=22)
        panel_w = min(1100, int(self.width * 0.92))
        panel_h = min(650, int(self.height * 0.85))
        self.shop_on = True
        if not self.shop:
            self.shop = self.shop_roll()

        root = agui.UIAnchorLayout()

        title = agui.UILabel(
            text="LUCKY CHARMS SHOP",
            font_name="HYDRA",
            font_size=28,
            text_color=(255, 210, 60),
            width=panel_w,
            height=40,
            align="center",
        )
        root.add(title, anchor_x="center", anchor_y="center", align_y=panel_h // 2 - 46)

        list_w = int(panel_w * 0.48)
        details_w = panel_w - list_w - 40
        ref_cost = self.shop_cost()
        info_label = agui.UILabel(
            text=f"Coins: {self.cash} | Tickets: {self.tk} | Refresh: {ref_cost} coins",
            font_name="QUICKSAND",
            font_size=16,
            text_color=(200, 200, 200),
            width=panel_w,
            height=24,
            align="center",
        )
        root.add(info_label, anchor_x="center", anchor_y="center", align_y=panel_h // 2 - 82)

        list_box = agui.UIBoxLayout(vertical=True, space_between=10, width=list_w, height=panel_h - 140)
        root.add(list_box, anchor_x="center", anchor_y="center", align_x=-(panel_w // 2) + 20 + list_w // 2, align_y=10)

        selected = {"id": self.shop[0] if self.shop else None}

        det_title = agui.UILabel(
            text="",
            font_name="HYDRA",
            font_size=22,
            text_color=(255, 210, 60),
            width=details_w - 24,
            height=30,
            align="left",
        )
        det_desc = agui.UILabel(
            text="",
            font_name="QUICKSAND",
            font_size=16,
            text_color=(235, 235, 235),
            width=details_w - 24,
            height=panel_h - 220,
            align="left",
        )
        root.add(
            det_title,
            anchor_x="center",
            anchor_y="center",
            align_x=(panel_w // 2) - 20 - details_w // 2 + 12,
            align_y=panel_h // 2 - 120,
        )
        root.add(
            det_desc,
            anchor_x="center",
            anchor_y="center",
            align_x=(panel_w // 2) - 20 - details_w // 2 + 12,
            align_y=10,
        )

        def ref_det():
            cid = selected["id"]
            if not cid:
                det_title.text = "—"
                det_desc.text = ""
                return
            ch = CHARM_LIBRARY[cid]
            owned = any(c.id == cid for c in self.charms.bag)
            det_title.text = f"{ch.name}   ({ch.cost} tickets)" + ("  [OWNED]" if owned else "")
            det_desc.text = ch.desc

        ref_det()

        for charm_id in self.shop:
            charm = CHARM_LIBRARY[charm_id]
            owned = any(c.id == charm_id for c in self.charms.bag)
            btn = agui.UIFlatButton(
                text=f"{charm.name} ({charm.cost} tickets)" + (" ✓" if owned else ""),
                width=list_w - 20,
                height=48,
                style=style,
                disabled=False,
            )

            @btn.event("on_click")
            def sel_handler(event, cid=charm_id):
                selected["id"] = cid
                ref_det()

            list_box.add(btn)

        btn_row = agui.UIBoxLayout(vertical=False, space_between=14)
        buy_btn = agui.UIFlatButton(text="BUY", width=180, height=58, style=style)
        ref_btn = agui.UIFlatButton(text=f"REFRESH (-{ref_cost}c)", width=220, height=58, style=style)
        close_btn = agui.UIFlatButton(text="CLOSE", width=180, height=58, style=style)

        @buy_btn.event("on_click")
        def _(_event):
            if selected["id"]:
                self.charm_buy(selected["id"])
                self.shop_on = False
                self.shop_show()

        @ref_btn.event("on_click")
        def _(_event):
            cost = self.shop_cost()
            if self.cash < cost:
                self.msg = "Not enough coins to refresh"
                return
            self.cash -= cost
            self.shopr += 1
            self.shop = self.shop_roll()
            self.msg = f"Shop refreshed (-{cost} coins)"
            self.shop_show()

        @close_btn.event("on_click")
        def _(_event):
            self.shop_on = False
            self.game_build()

        btn_row.add(buy_btn)
        btn_row.add(ref_btn)
        btn_row.add(close_btn)
        root.add(btn_row, anchor_x="center", anchor_y="center", align_y=-(panel_h // 2) + 54)

        try:
            self.ui.children.clear()
        except Exception:
            pass
        self.ui.add(root)

    def fin_build(self):
        rest_btn = agui.UIFlatButton(text="Restart", width=200, height=60, style=btn_style)
        menu_btn = agui.UIFlatButton(text="Menu", width=200, height=60, style=btn_style)

        @rest_btn.event("on_click")
        def _(_event):
            self.rst()
            self.st = "game"
            self.game_build()

        @menu_btn.event("on_click")
        def _(_event):
            self.menu()

        if self.ui:
            self.ui.disable()
        self.ui = agui.UIManager(self)
        self.ui.enable()
        layout = agui.UIBoxLayout(vertical=True, space_between=12)
        layout.add(rest_btn)
        layout.add(menu_btn)
        anchor = agui.UIAnchorLayout()
        anchor.add(child=layout, anchor_x="center", anchor_y="center")
        self.ui.add(anchor)

    def hud(self):
        pad = 20
        hud_box = arcade.LBWH(self.width - 360 - pad, self.height - 260, 360, 240)
        arcade.draw_rect_outline(hud_box, (255, 210, 60), border_width=3)
        info = [
            f"Coins: {self.cash}",
            f"Tickets: {self.tk}",
            f"Spins left: {self.spin_left}",
            f"Debt: {self.dbt}",
            f"Level: {self.lv}",
            f"Luck: {self.luck}",
            f"Interest: {self.rt}%",
            f"Charms: {len(self.charms.bag)}",
        ]
        start_y = self.height - pad - 50
        for i, text in enumerate(info):
            arcade.draw_text(text, self.width - 360, start_y - i * 26, (235, 235, 235), 18, font_name="CAUSE")
        arcade.draw_text(self.msg, pad, self.height - 70, (255, 210, 60), 18, font_name="QUICKSAND")
        if self.last:
            ls = self.last
            text = f"+{ls['coins']} coins | +{ls['tk']} tickets | {ls['patterns']} patterns"
            arcade.draw_text(text, pad, pad + 60, (180, 220, 255), 16, font_name="QUICKSAND")
        self.charms_draw()

    def charms_draw(self):
        x = 20
        y = 120
        for charm in self.charms.bag:
            line = charm.name
            if charm.trg_type == CharmTriggerType.RED_BUTTON:
                line += f" [{charm.charges}/{charm.max_chg}]"
            arcade.draw_text(line, x, y, (200, 200, 200), 18, font_name="CAUSE")
            y += 22

    def hl_draw(self):
        if not self.hl or self.hi >= len(self.hl):
            return
        positions = self.hl[self.hi]
        for row, col in positions:
            cell = self.cells[row][col]
            sprite = cell.sprite
            if not sprite:
                continue
            width = sprite.width * 1.15
            height = sprite.height * 1.15
            left1 = sprite.center_x - width / 2
            bottom1 = sprite.center_y - height / 2
            left2 = sprite.center_x - (width + 8) / 2
            bottom2 = sprite.center_y - (height + 8) / 2
            arcade.draw_lbwh_rectangle_outline(left1, bottom1, width, height, (255, 220, 90), border_width=4)
            arcade.draw_lbwh_rectangle_outline(left2, bottom2, width + 8, height + 8, (60, 170, 255), border_width=2)

    def fin_draw(self):
        arcade.draw_lrbt_rectangle_filled(0, self.width, 0, self.height, (12, 12, 18))
        if not self.fin:
            return
        summary = self.fin
        arcade.draw_text("You failed to pay the debt.", self.width // 2 - 260, self.height - 160, (255, 200, 60), 32, font_name="HYDRA")
        lines = [
            f"Level reached: {summary['lv']}",
            f"Coins banked: {summary['cash']}",
            f"Debt remaining: {summary['dbt']}",
            f"Tickets saved: {summary['tk']}",
            f"Interest: {summary['rt']}%",
        ]
        for i, text in enumerate(lines):
            arcade.draw_text(text, self.width // 2 - 200, self.height - 220 - i * 30, (220, 220, 220), 20, font_name="QUICKSAND")

    def on_draw(self):
        self.clear((8, 10, 12))
        if self.st == "menu" or self.st == "cfg":
            self.ui.draw()
            return
        if self.st == "game":
            self.cam_sync()

            shk_x, shk_y = 0, 0
            if self.shk > 0:
                shk_x = random.randint(-6, 6)
                shk_y = random.randint(-4, 4)

            if self.bg:
                rect = arcade.LBWH(shk_x, shk_y, self.width, self.height)
                arcade.draw_texture_rect(self.bg, rect)
            else:
                back = arcade.LBWH(shk_x, shk_y, self.width, self.height)
                arcade.draw_rect_filled(back, (15, 17, 20))

            box_shkn = arcade.LBWH(
                self.box.left + shk_x,
                self.box.bottom + shk_y,
                self.box.width,
                self.box.height,
            )
            arcade.draw_rect_filled(box_shkn, (20, 20, 24))
            inner_box = arcade.LBWH(
                box_shkn.left + 10,
                box_shkn.bottom + 10,
                box_shkn.width - 20,
                box_shkn.height - 20,
            )
            arcade.draw_rect_outline(inner_box, (255, 210, 60), border_width=3)
            if self.stx:
                arcade.draw_texture_rect(self.stx, inner_box)

            for sprite in self.spr:
                if not sprite or not getattr(sprite, "texture", None):
                    continue
                arcade.draw_sprite(sprite)

            self.hl_draw()

            for p in self.pt:
                arcade.draw_circle_filled(p["x"] + shk_x, p["y"] + shk_y, p["size"], p["color"])

            self.hud()
            if self.shop_on:
                arcade.draw_lrbt_rectangle_filled(0, self.width, 0, self.height, (0, 0, 0, 220))
            self.ui.draw()
        if self.st == "final":
            self.fin_draw()
            if self.ui:
                self.ui.draw()

    def on_update(self, delta_time: float):
        if self.st != "game":
            return
        if self.spin_on and time.time() >= self.spin_t:
            self.spin_end()
        elif self.spin_on:
            for row in self.cells:
                for cell in row:
                    if cell.sprite:
                        cell.sprite.texture = random.choice(list(self.tx.values()))
        self.update_pt(delta_time)
        if self.hl:
            self.ht += delta_time
            if self.ht >= self.hlen:
                self.ht = 0.0
                if self.hi + 1 < len(self.hl):
                    self.hi += 1
                else:
                    self.hl = []
                    self.hi = 0
        if self.shk > 0:
            self.shk -= delta_time
        if self.tk < 0:
            self.tk = 0
        if self.lt_sp_left > 0 and not self.spin_on and self.st == "game":
            self.lt_sp_left -= 1
            if self.lt_sp_left <= 0:
                self.ltemp = 0
        if self.spin_left <= 0 and not self.spin_on and self.st == "game":
            self.dead_end()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.spin_go()
        if key == arcade.key.R:
            self.red_go()

    def on_mouse_press(self, x, y, button, modifiers):
        try:
            if self.ui and self.ui.dispatch_event("on_mouse_press", x, y, button, modifiers):
                return True
        except Exception:
            pass
        self.charm_hit(x, y)
        return False

    def charm_hit(self, x: float, y: float):
        if self.st != "game":
            return
        start_x = 20
        start_y = 120
        line_ht = 22
        for idx, charm in enumerate(self.charms.bag):
            cy = start_y + idx * line_ht
            if start_x <= x <= start_x + 200 and cy <= y <= cy + line_ht:
                dialog = agui.UIMessageBox(
                    width=360,
                    height=180,
                    message_text=f"Remove {charm.name}?",
                    buttons=["Yes", "No"],
                )

                @dialog.event("on_action")
                def _on_action(event, cid=charm.id):
                    if event.action == "Yes":
                        self.drop_ok("Yes", cid)
                    try:
                        dialog.parent.remove(dialog)
                    except Exception:
                        pass

                self.ui.add(dialog)
                break

    def drop_ok(self, value: str, charm_id: str):
        if value != "Yes":
            return
        self.charms.unadd(charm_id)
        self.rt_upd()
        self.mult_sync()

    def rt_upd(self):
        base_int = self.cfg["InitInterest"]
        charm_int = self.charms.val("int_boost")
        self.rt = base_int + charm_int

    def mult_sync(self):
        old_static = getattr(self, "static_sm", 0)
        growth = max(0.0, self.sm - (self.cfg["InitMultiply"] + old_static))
        new_static = self.charms.val("symbol_multiplier")
        self.static_sm = new_static
        self.sm = self.cfg["InitMultiply"] + self.static_sm + growth

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.cam_sync()
        self.grid_build()
        if self.st == "game":
            self.game_build()

    def cam_sync(self):
        try:
            if hasattr(self, "ctx") and hasattr(self.ctx, "viewport"):
                self.ctx.viewport = (0, 0, int(self.width), int(self.height))
        except Exception:
            pass

























