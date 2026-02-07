import json
import os
from pathlib import Path

import arcade
from arcade.gui import UIFlatButton

SETTINGS_PATH = Path("Data/assets/gamesettings.json")

DEFAULT_SETTINGS = {
    "WWidth": 1280,
    "WHeight": 720,
    "WTitle": "LastDep",
    "WFullScreen": False,
    "InitSatoshi": 120,
    "Initspin_left": 7,
    "Initrnds": 3,
    "InitDebt": 120,
    "InitMultiply": 1,
    "InitComMultiply": 1,
    "InitTickets": 4,
    "InitInterest": 10,
    "InitCharmSlots": 4,
    "InitLuck": 6,
    "Enablept": True,
    "Enableshk": True,
}


def load_config():
    data = DEFAULT_SETTINGS.copy()
    if SETTINGS_PATH.exists():
        try:
            data.update(json.loads(SETTINGS_PATH.read_text(encoding="utf-8")))
        except Exception:
            pass
    if "Initspin_left" not in data and "InitSpins" in data:
        data["Initspin_left"] = data.get("InitSpins", DEFAULT_SETTINGS["Initspin_left"])
    if "Initrnds" not in data and "InitRounds" in data:
        data["Initrnds"] = data.get("InitRounds", DEFAULT_SETTINGS["Initrnds"])
    if "Enablept" not in data and "EnableParticles" in data:
        data["Enablept"] = data.get("EnableParticles", DEFAULT_SETTINGS["Enablept"])
    if "Enableshk" not in data and "EnableShake" in data:
        data["Enableshk"] = data.get("EnableShake", DEFAULT_SETTINGS["Enableshk"])
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def save_config(data):
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


config = load_config()

WINSET = {
    "W": config["WWidth"],
    "H": config["WHeight"],
    "T": config["WTitle"],
    "F": config["WFullScreen"],
}

COL = {
    "Y": (255, 200, 0)
}

TTF = {
    "HYDRA": os.path.abspath("./Data/assets/ttf/HYDRA.TTF"),
    "QUICKSAND": os.path.abspath("./Data/assets/ttf/QUICKSAND.TTF"),
    "CAUSE": os.path.abspath("./Data/assets/ttf/cause.ttf"),
}

btn_style = {
    "normal": UIFlatButton.UIStyle(
        font_size=32,
        font_name="CAUSE",
        bg=arcade.color.TRANSPARENT_BLACK,
        border=None,
    ),
    "hover": UIFlatButton.UIStyle(
        font_size=32,
        font_name="CAUSE",
        font_color=arcade.color.YELLOW,
        bg=arcade.color.TRANSPARENT_BLACK,
        border=None,
    ),
    "press": UIFlatButton.UIStyle(
        font_size=32,
        font_name="CAUSE",
        font_color=arcade.color.ORANGE,
        bg=arcade.color.TRANSPARENT_BLACK,
        border=None,
    )
}

