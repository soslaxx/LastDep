import json
from pathlib import Path
from typing import Dict, Any

SAVE_DIR = Path("Data/saves")
STATS_PATH = SAVE_DIR / "stats.json"


def _def_stats() -> Dict[str, Any]:
    return {
        "tot_runs": 0,
        "tot_spins": 0,
        "tot_coins": 0,
        "tot_tk": 0,
        "best_bal": 0,
        "best_lvl": 0,
        "best_pat_win": 0,
    }


def load_stats() -> Dict[str, Any]:
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    if STATS_PATH.exists():
        try:
            stats = json.loads(STATS_PATH.read_text(encoding="utf-8"))
            return stats
        except Exception:
            pass
    stats = _def_stats()
    STATS_PATH.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    return stats


def save_stats(update: Dict[str, Any]) -> None:
    stats = load_stats()
    stats["tot_runs"] = stats.get("tot_runs", 0) + update.get("runs", 0)
    stats["tot_spins"] = stats.get("tot_spins", 0) + update.get("spins", 0)
    stats["tot_coins"] = stats.get("tot_coins", 0) + update.get("coins", 0)
    stats["tot_tk"] = stats.get("tot_tk", 0) + update.get("tickets", 0)
    stats["best_bal"] = max(stats.get("best_bal", 0), update.get("balance", 0))
    stats["best_lvl"] = max(stats.get("best_lvl", 0), update.get("level", 0))
    stats["best_pat_win"] = max(stats.get("best_pat_win", 0), update.get("max_pat_coins", 0))
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    STATS_PATH.write_text(json.dumps(stats, indent=2), encoding="utf-8")


def load_best() -> str:
    stats = load_stats()
    return (
        f"Best level: {stats['best_lvl']} | "
        f"Best balance: {stats['best_bal']} | "
        f"Max combo payout: {stats['best_pat_win']}"
    )

