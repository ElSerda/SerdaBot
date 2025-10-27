# backends.game_lookup

**Migré depuis**: `backends/game_lookup.py`  
**Lignes doc originales**: 14  
**Éléments over-engineered**: 0  

---

## Module Overview

```text

SerdaBot V1 - Game Lookup API multi-sources (RAWG + Steam) - Architecture KISS.

```

## API Reference

### Standard Components

#### GameLookup (class)

```text

Gestionnaire principal des recherches de jeux multi-API.

```

#### GameResult (class)

```text

Résultat de jeu avec validation de fiabilité et données enrichies.

```

#### _calculate_reliability (func)

```text

Calcule le score de fiabilité - Version KISS avec boost précision.

```

#### _extract_year (func)

```text

Extrait l'année d'une date ISO.

```

#### _fetch_rawg (func)

```text

Récupère données depuis RAWG API.

```

#### _fetch_steam (func)

```text

Récupère données depuis Steam API.

```

#### _find_best_game_lean (func)

```text

Trouve le jeu le plus pertinent - Version LEAN simplifiée.

```

#### _get_confidence_level (func)

```text

Détermine le niveau de confiance - Version LEAN simplifiée.

```

#### _merge_data (func)

```text

Fusionne les données RAWG + Steam - Version LEAN.

```

#### _validate_game_data (func)

```text

Valide les données de jeu - Version LEAN simplifiée.

```

#### close (func)

```text

Nettoyage à la fermeture.

```

#### format_result (func)

```text

Formate le résultat pour affichage Twitch - Version LEAN.

```

#### search_game (func)

```text

Point d'entrée principal pour recherche de jeu.

```
