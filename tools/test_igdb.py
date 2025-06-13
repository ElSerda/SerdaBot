# tools/test_igdb.py
# --------------------------------------
# Script de test local IGDB avec ou sans modèle IA
# Version finale commentée avec gestion consolidée des plateformes
# --------------------------------------

import asyncio
from datetime import datetime
from typing import Optional, Union

from config.config import load_config
from core.igdb_api import get_igdb_token, query_game, search_igdb_web


def compress_platforms(platforms: Union[list, str]) -> list[str]:
    """
    Raccourcit les noms de plateformes connues via un mapping.
    Supprime les doublons tout en conservant l'ordre d'origine.
    """

    def normalize(p):
        try:
            return str(p).strip()
        except Exception:
            return "Autre"

    mapping = {
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
        dict.fromkeys(mapping.get(normalize(p), normalize(p)) for p in platforms)
    )


async def main():
    print("🧠 Activer la traduction IA ? (y/n) : ", end="")
    use_model = input().strip().lower() == "y"

    config: Optional[dict] = load_config() if use_model else None

    game_name = input("Nom du jeu IGDB à rechercher : ").strip()
    token = get_igdb_token()
    game_data = query_game(game_name, token)

    if not game_data and config:
        game_data = await search_igdb_web(game_name, config)

    if not game_data:
        print("❌ Aucun résultat trouvé.")
        return

    name = game_data.get("name", "Nom inconnu")
    raw_summary = game_data.get("summary", "Résumé non disponible")
    release_date = game_data.get("first_release_date")
    platforms = game_data.get("platforms", [])
    genres = game_data.get("genres", [])

    # 🧠 Traitement structuré des plateformes selon leur type
    if isinstance(platforms, list):
        # ✅ Cas 1 : fallback HTML → liste de caractères → on reconstruit une chaîne puis on split
        if all(isinstance(p, str) and len(p) == 1 for p in platforms):
            platforms = "".join(platforms).split(",")
            platforms = [p.strip() for p in platforms]

        # ✅ Cas 2 : liste d’objets dict → extraction des noms via "name"
        elif all(isinstance(p, dict) and "name" in p for p in platforms):
            platforms = [p["name"] for p in platforms]

    # ✅ Cas 3 : string brute (non listée) → split direct
    elif isinstance(platforms, str):
        platforms = [p.strip() for p in platforms.split(",")]

    # 🧼 Nettoyage du résumé (1er paragraphe uniquement, sans doublon de nom)
    clean = raw_summary.strip().split("\n\n")[0]
    lowered = clean.lower().replace("’", "'")
    if name.lower() in lowered:
        clean = (
            clean.replace(name, "")
            .replace(name + " ", "")
            .strip()
            .lstrip(".")
            .lstrip(":")
        )
    summary = clean.strip()

    # 🌍 Traduction IA si activée
    if use_model and config:
        try:
            from utils.llm import clean_response, translate_summary

            translated = await translate_summary(summary, config)
            summary = clean_response(translated or "", max_length=None)
        except Exception as e:
            print(f"⚠️ Erreur de traduction : {e}")

    # 🗓️ Formatage de la date de sortie (si connue uniquement)
    if release_date:
        try:
            date = datetime.utcfromtimestamp(release_date).strftime("%Y-%m-%d")
        except Exception:
            date = None
    else:
        date = None

    # 🎮 Compression des noms de plateformes
    platforms = compress_platforms(platforms)

    # 🖨️ Affichage final
    print("\n🎮 Informations sur le jeu :\n")
    print(f"Nom         : {name}")
    print(f"Résumé      : {summary}")
    if date:
        print(f"Sortie      : {date}")
    print(f"Plateformes : {', '.join(platforms) if platforms else 'Aucune'}")
    if genres:
        print(f"Genres      : {', '.join(genres)}")


if __name__ == "__main__":
    asyncio.run(main())
