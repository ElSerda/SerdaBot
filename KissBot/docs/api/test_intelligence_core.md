# tests.test_intelligence_core

**Migré depuis**: `tests/test_intelligence_core.py`  
**Lignes doc originales**: 15  
**Éléments over-engineered**: 0  

---

## Module Overview

```text


Tests unitaires de intelligence.core - Logique métier pure
Ces tests sont SIMPLES car pas de dépendance TwitchIO !

```

## API Reference

### Standard Components

#### TestExtractors (class)

```text

Tests des extracteurs de texte (fonctions pures).

```

#### TestProcessLLMRequest (class)

```text

Tests du processeur LLM (logique métier).

```

#### test_context_ask_vs_mention (func)

```text

Test que les contexts sont correctement passés.

```

#### test_extract_mention_invalid (func)

```text

Test extraction mention invalide.

```

#### test_extract_mention_valid (func)

```text

Test extraction mention valide.

```

#### test_extract_question_invalid (func)

```text

Test extraction question invalide.

```

#### test_extract_question_valid (func)

```text

Test extraction question valide.

```

#### test_process_llm_empty_response (func)

```text

Test réponse vide.

```

#### test_process_llm_exception (func)

```text

Test gestion exception.

```

#### test_process_llm_success (func)

```text

Test traitement LLM réussi.

```

#### test_process_llm_truncate (func)

```text

Test truncate réponse trop longue.

```
