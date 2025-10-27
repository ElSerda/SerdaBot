# core.handlers

**Migré depuis**: `core/handlers.py`  
**Lignes doc originales**: 48  
**Éléments over-engineered**: 0  

---

## Module Overview

```text

Pure business logic handlers, framework-independent. See: docs/api/handlers.md

```

## API Reference

### Standard Components

#### CacheHandler (class)

```text

Handler pour les commandes cache

```

#### GameInfoHandler (class)

```text

Handler pour les infos de jeu

```

#### HandlersFactory (class)

```text

Factory pour créer handlers avec config

```

#### HelpHandler (class)

```text

Handler pour l'aide

```

#### LatencyHandler (class)

```text

Handler pour mesurer la latence de traitement.

```

#### PingHandler (class)

```text

Handler pour la commande ping

```

#### QuantumPipelineHandler (class)

```text

Handler pour le pipeline quantique

```

#### StatsHandler (class)

```text

Handler pour les statistiques

```

#### TranslationHandler (class)

```text

Handler pour la traduction

```

#### __init__ (func)

```text

Initialise avec le timestamp de début.

```

#### _format_game_response (func)

```text

Formate la réponse de jeu

```

#### get_cache_response (func)

```text

Génère réponse cache détaillée

```

#### get_help_response (func)

```text

Génère liste des commandes

```

#### get_latency_response (func)

```text

Calcule et retourne la latence en microsecondes.

```

#### get_ping_response (func)

```text

Génère réponse ping avec uptime

```

#### get_quantum_pipeline_response (func)

```text

Génère réponse stats pipeline quantique

```

#### get_stats_response (func)

```text

Génère réponse stats complète

```

#### observe_user_message (func)

```text


        Observe un message utilisateur (logique quantique)
        
        Returns:
            État après observation

```

#### search_game_info (func)

```text


        Recherche informations sur un jeu
        
        Returns:
            (success, response_message)

```

#### translate_text (func)

```text


        Traduit le texte vers français
        
        Returns:
            (success, translated_text_or_error)

```

#### validate_game_query (func)

```text


        Valide et extrait la requête de jeu
        
        Returns:
            (is_valid, game_name, error_message)

```

#### validate_translation_query (func)

```text


        Valide et extrait le texte à traduire
        
        Returns:
            (is_valid, text_to_translate, error_message)

```
