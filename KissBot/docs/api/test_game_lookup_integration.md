# tests.backends.test_game_lookup_integration

**Migré depuis**: `tests/backends/test_game_lookup_integration.py`  
**Lignes doc originales**: 29  
**Éléments over-engineered**: 0  

---

## Module Overview

```text


Tests d'intégration pour backends/game_lookup.py
Tests avec cas réels pour détecter les bugs

```

## API Reference

### Standard Components

#### TestGameLookupBugFixes (class)

```text

Tests pour bugs identifiés en production.

```

#### TestGameLookupEdgeCases (class)

```text

Tests cas limites et edge cases.

```

#### TestGameLookupIntegration (class)

```text

Tests d'intégration avec cas réels.

```

#### game_lookup (func)

```text

Fixture GameLookup avec config mock.

```

#### test_bug_bye_sweet_carole (func)

```text


        BUG: "Bye Sweet Carole" ne renvoyait que "platform pc" dans SerdaBot.
        
        Expected: Nom complet, année, rating, genres
        Actual (SerdaBot): Seulement "platform pc"

```

#### test_itch_io_game (func)

```text


        Test jeu itch.io - Celeste Classic (jeu indie célèbre sur itch.io).
        
        Vérifie que KissBot peut trouver des jeux itch.io indie.

```

#### test_search_empty_string (func)

```text

Test recherche chaîne vide.

```

#### test_search_game_with_year (func)

```text

Test recherche avec année dans le nom.

```

#### test_search_nonexistent_game (func)

```text

Test jeu inexistant.

```

#### test_search_only_spaces (func)

```text

Test recherche espaces seulement.

```

#### test_search_popular_game (func)

```text

Test recherche jeu populaire (Elden Ring).

```

#### test_search_short_name (func)

```text

Test jeu avec nom court (peut causer ambiguïté).

```

#### test_search_unicode_characters (func)

```text

Test caractères unicode.

```

#### test_search_very_long_name (func)

```text

Test nom très long (100+ chars).

```

#### test_search_with_special_characters (func)

```text

Test jeu avec caractères spéciaux.

```

#### test_search_with_typo (func)

```text

Test recherche avec faute de frappe.

```
