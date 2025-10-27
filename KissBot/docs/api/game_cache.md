# backends.game_cache

**Migré depuis**: `backends/game_cache.py`  
**Lignes doc originales**: 34  
**Éléments over-engineered**: 0  

---

## Module Overview

**(Documentation originale over-engineered - migrated from inline)**

```text


🎮 Game Cache Classique - KissBot V1

Cache système optimisé pour les données de jeux.
Archi parallèle au QuantumGameCache pour compatibilité.

FONCTIONNALITÉS :
├── Cache simple et efficace
├── Gestion TTL automatique  
├── Nettoyage expired intelligent
├── Compatibilité config standard
└── Fallback pour système quantique

```

## API Reference

### Standard Components

#### GameCache (class)

```text


    Cache Classique pour les jeux - Architecture parallèle au QuantumCache
    
    WORKFLOW CLASSIQUE :
    - Recherche directe par clé
    - TTL fixe configurable
    - Pas d'apprentissage adaptatif
    - Cache simple mais robuste

```

#### _ensure_cache_dir (func)

```text

Créer le dossier cache si nécessaire.

```

#### _load_cache (func)

```text

Charger le cache depuis le fichier.

```

#### _save_cache (func)

```text

Sauvegarder le cache.

```

#### cleanup_expired (func)

```text

Nettoie les entrées expirées.

```

#### clear (func)

```text

Vide le cache compatible interface.

```

#### clear_all (func)

```text

Vider complètement le cache.

```

#### clear_expired (func)

```text

Nettoyer les entrées expirées.

```

#### clear_game (func)

```text

Supprimer un jeu spécifique du cache.

```

#### get (func)

```text

Récupérer un jeu du cache.

```

#### get_stats (func)

```text

Stats du cache compatible interface.

```

#### search (func)

```text

Recherche compatible interface (délégue vers get).

```

#### set (func)

```text

Mettre en cache un jeu - Interface BaseCacheInterface.

```
