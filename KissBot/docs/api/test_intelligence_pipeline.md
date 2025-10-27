# tests.test_intelligence_pipeline

**Migré depuis**: `tests/test_intelligence_pipeline.py`  
**Lignes doc originales**: 30  
**Éléments over-engineered**: 0  

---

## Module Overview

```text


Tests unitaires du pipeline Intelligence
Détecte les bugs de context et de partage d'instance LLMHandler

```

## API Reference

### Standard Components

#### TestIntelligencePipeline (class)

```text

Tests du pipeline Intelligence (commands + events).

```

#### TestPipelineIntegration (class)

```text

Tests d'intégration du pipeline complet.

```

#### mock_bot (func)

```text

Mock bot TwitchIO.

```

#### mock_context (func)

```text

Mock TwitchIO context pour !ask.

```

#### mock_message (func)

```text

Mock TwitchIO message pour @mention.

```

#### test_ask_command_uses_correct_context (func)

```text


        BUG DÉTECTÉ: !ask doit utiliser context='ask', pas 'command'

```

#### test_ask_to_mention_context_difference (func)

```text


        Test que !ask et @mention utilisent des contexts différents

```

#### test_contexts_available (func)

```text


        Test que les contexts 'ask' et 'mention' sont bien définis
        (pas de 'command' ou 'chill' obsolètes)

```

#### test_intelligence_cog_init (func)

```text

Test que IntelligenceCommands initialise correctement le LLMHandler.

```

#### test_mention_uses_correct_context (func)

```text


        Test que @mention utilise context='mention'

```

#### test_personality_flags_propagation (func)

```text


        Test que les flags de personality sont bien propagés au LLMHandler

```

#### test_shared_llm_handler_instance (func)

```text


        BUG DÉTECTÉ: events.py ne doit PAS créer une nouvelle instance LLMHandler
        Il doit réutiliser celle du Cog

```
