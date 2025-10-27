# tests.intelligence.test_anti_hallucination

**Migré depuis**: `tests/intelligence/test_anti_hallucination.py`  
**Lignes doc originales**: 11  
**Éléments over-engineered**: 0  

---

## Module Overview

```text


Tests anti-hallucination pour LLMHandler.
Valide que les prompts minimaux réduisent les hallucinations.

```

## API Reference

### Standard Components

#### llm_handler (func)

```text

Charge le handler avec config réelle.

```

#### test_ask_factual_response (func)

```text

Test qu'une question factuelle obtient une réponse factuelle.

```

#### test_mention_ultra_short (func)

```text

Test que les mentions restent ultra-courtes (<= 200 chars).

```

#### test_minimal_prompt_format (func)

```text

Test que les prompts sont bien minimaux (structure).

```

#### test_response_length_limits (func)

```text

Test que toutes les réponses respectent les limites de caractères.

```

#### test_simple_greeting_concise (func)

```text

Test que 'salut !' reste concis sans narratif excessif.

```

#### test_tournevis_no_hallucination (func)

```text

Test que la question 'c'est quoi un tournevis ?' ne hallucine pas.

```
