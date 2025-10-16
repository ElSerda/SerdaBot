import logging
import re
import unicodedata
from datetime import datetime

from langdetect import detect

from core.igdb_api import get_igdb_token, query_game, search_igdb_web


def normalize_platforms(platforms):
    if isinstance(platforms, list):
        if all(isinstance(plat, str) and len(plat) == 1 for plat in platforms):
            return [plat.strip() for plat in "".join(platforms).split(",")]
        elif all(isinstance(plat, dict) and "name" in plat for plat in platforms):
            return [plat["name"] for plat in platforms]
    elif isinstance(platforms, str):
        return [plat.strip() for plat in platforms.split(",")]
    return platforms


def compress_platforms(platforms):
    mapping = {
        "Google Stadia": "Stadia",
        "Xbox Series X|S": "Xbox",
        "Xbox One": "Xbox",
        "Nintendo Switch 2": "Switch 2",
        "Nintendo Switch": "Switch",
        "PC (Microsoft Windows)": "PC",
        "Mac": "Mac",
        "PlayStation 5": "PS5",
        "PlayStation 4": "PS4",
        "PlayStation 3": "PS3",
    }
    return list(
        dict.fromkeys(mapping.get(str(plat).strip(), str(plat).strip()) for plat in platforms)
    )


def clean_summary(summary: str, game_name: str) -> str:
    clean = summary.strip().split("\n\n")[0]
    pattern = re.compile(re.escape(game_name), re.IGNORECASE)
    clean = pattern.sub("", clean).strip().lstrip(".:").strip()
    return clean


def sanitize_slug(slug: str) -> str:
    slug = unicodedata.normalize("NFKD", slug).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9-]", "", slug.replace(" ", "-").lower())


def format_igdb_url(name: str, slug: str = "") -> str:
    return f"https://www.igdb.com/games/{sanitize_slug(slug or name)}"


def format_date(ts: int) -> str:
    return datetime.utcfromtimestamp(ts).strftime("%Y") if ts else "?"


async def fetch_steam_summary(game_name: str, config: dict):
    try:
        from utils.steam import search_steam_summary

        result = await search_steam_summary(game_name, config)
        if result:
            print(f"[METRICS-GAME] 📥 Steam: {len(result)} chars summary")
        else:
            print("[METRICS-GAME] ⚠️ Steam: aucun résumé trouvé")
        return result
    except Exception as e:
        print(f"[METRICS-GAME] ❌ Steam error: {e}")
        return ""


async def fetch_game_data(game_name: str, config: dict) -> dict:
    print(f"[METRICS-GAME] 🔍 Recherche: '{game_name}'")
    token = get_igdb_token()
    data = query_game(game_name, token)
    if data:
        logging.debug("✅ IGDB API utilisée.")
        summary_len = len(data.get('summary', ''))
        print(f"[METRICS-GAME] 📥 IGDB API: {summary_len} chars summary")
        return data

    data = await search_igdb_web(game_name, config)
    if data:
        logging.debug("⚠️ Fallback IGDB web utilisé.")
        summary_len = len(data.get('summary', ''))
        print(f"[METRICS-GAME] 📥 IGDB Web Scraping: {summary_len} chars summary")
        return data

    print("[METRICS-GAME] ❌ Aucune donnée trouvée")
    return {}


async def choose_best_summary(
    name: str, igdb_summary: str, steam_summary: str
) -> tuple[str, str, str, str]:
    try:
        detected_igdb = detect(igdb_summary) if igdb_summary else "und"
    except Exception:
        detected_igdb = "und"

    try:
        detected_steam = detect(steam_summary) if steam_summary else "und"
    except Exception:
        detected_steam = "und"

    if detected_igdb == "fr":
        return igdb_summary, "IGDB (FR)", detected_igdb, detected_steam
    elif detected_steam == "fr":
        return steam_summary, "Steam (FR)", detected_igdb, detected_steam
    else:
        summary = (
            igdb_summary
            if len(igdb_summary) <= len(steam_summary or "")
            else steam_summary or igdb_summary
        )
        return summary, "fallback (shortest)", detected_igdb, detected_steam
