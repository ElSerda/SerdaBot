# tests.test_unit_commands

**Migré depuis**: `tests/test_unit_commands.py`  
**Lignes doc originales**: 24  
**Éléments over-engineered**: 0  

---

## Module Overview

```text


🧪 Tests Unitaires Commands - KissBot V1

Test de chaque commande individuellement avec mocks appropriés.
Validation des comportements quantiques et classiques.

```

## API Reference

### Standard Components

#### TestGameCommands (class)

```text

Tests pour les commandes de jeu classiques

```

#### TestQuantumCommands (class)

```text

Tests pour les commandes quantiques

```

#### TestTranslationCommands (class)

```text

Tests pour les commandes de traduction

```

#### TestUtilsCommands (class)

```text

Tests pour les commandes utilitaires

```

#### setup_method (func)

```text

Setup pour chaque test

```

#### test_game_info_low_confidence_rejection (func)

```text

Test rejet des résultats LOW confidence

```

#### test_game_info_no_param (func)

```text

Test !gameinfo sans paramètre

```

#### test_game_info_quantum_fallback (func)

```text

Test fallback quantique → classique

```

#### test_game_info_success (func)

```text

Test !gameinfo avec succès

```

#### test_help_command (func)

```text

Test !help

```

#### test_observe_missing_key (func)

```text

Test !observe sans paramètre

```

#### test_observe_state (func)

```text

Test !observe <clé>

```

#### test_ping_command (func)

```text

Test !ping

```

#### test_quantum_status (func)

```text

Test !quantum status

```

#### test_stats_command (func)

```text

Test !stats avec cache stats

```

#### test_translate_api_error (func)

```text

Test !trad avec erreur API

```

#### test_translate_no_text (func)

```text

Test !trad sans texte

```

#### test_translate_success (func)

```text

Test !trad avec succès

```
