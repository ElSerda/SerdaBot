# tests.intelligence.test_smart_context

**Migré depuis**: `tests/intelligence/test_smart_context.py`  
**Lignes doc originales**: 15  
**Éléments over-engineered**: 0  

---

## Module Overview

```text


Tests unitaires pour Smart Context - KissBot V1
ATTENTION: Ces tests vérifient la logique Smart Context en isolation.
Pour tester le pipeline complet, voir test_pipeline_integration.py

```

## API Reference

### Standard Components

#### MockGameCache (class)

```text

Mock du GameCache pour tests unitaires SEULEMENT.

```

#### get (func)

```text

Simulation de la méthode get du GameCache

```

#### test_enrich_prompt_with_game_context_no_game (func)

```text

Test enrichissement prompt sans jeu trouvé.

```

#### test_enrich_prompt_with_game_context_not_game_question (func)

```text

Test avec question qui n'est pas sur un jeu.

```

#### test_enrich_prompt_with_game_context_with_game (func)

```text

Test enrichissement prompt avec jeu trouvé.

```

#### test_find_game_in_cache_empty_cache (func)

```text

Test avec cache vide.

```

#### test_find_game_in_cache_exact_match (func)

```text

Test avec nom exact du jeu.

```

#### test_find_game_in_cache_fuzzy_match (func)

```text

Test avec faute de frappe (fuzzy matching).

```

#### test_find_game_in_cache_no_match (func)

```text

Test avec jeu non trouvé.

```

#### test_run_all_tests (func)

```text

Lance tous les tests et affiche le résultat.

```
