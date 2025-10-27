# intelligence.handler

**Migré depuis**: `intelligence/handler.py`  
**Lignes doc originales**: 15  
**Éléments over-engineered**: 0  

---

## Module Overview

```text


KissBot V1 - LLM Handler KISS avec cascade fallback + Model-Specific Prompting
Version simplifiée inspirée de SerdaBot avec randomizer El_Serda + optimisation prompts !

```

## API Reference

### Standard Components

#### LLMHandler (class)

```text

Handler LLM KISS avec cascade à 3 niveaux.

```

#### ModelPromptOptimizer (class)

```text

Optimiseur de prompts par modèle - Version KISS.

```

#### _check_local_health (func)

```text

🏥 Health check rapide du LLM local (2s max).

```

#### _detect_model_type (func)

```text

Détecte le type de modèle en cours d'utilisation - Version KISS.

```

#### _get_fun_fallback (func)

```text

Répliques de fallback simples.

```

#### _try_local (func)

```text

Essai Local LM Studio avec health check préalable.

```

#### _try_openai (func)

```text

Essai OpenAI avec gestion d'erreur et quota.

```

#### generate_response (func)

```text

Génère une réponse LLM avec fallback cascade.

```

#### get_fallback_response (func)

```text

Fallback statique simple.

```

#### get_system_prompt (func)

```text

Retourne le prompt système optimisé par PROVIDER.

```

#### update_bot_name (func)

```text

🔄 Met à jour le nom du bot avec le vrai nom TwitchIO.

```
