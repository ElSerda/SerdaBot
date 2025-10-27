# intelligence.core

**Migré depuis**: `intelligence/core.py`  
**Lignes doc originales**: 59  
**Éléments over-engineered**: 3  

---

## Module Overview

```text


Intelligence Core - Logique métier pure (facile à tester)
Séparation business logic / framework TwitchIO

```

## API Reference

### 🚨 Over-engineered Components (migrated)

#### process_llm_request (func)

**Original doc**: 13 lines, 0 quantum terms


```text


    Traite une requête LLM - Logique métier pure.
    
    Args:
        llm_handler: Instance LLMHandler
        prompt: Question/message de l'utilisateur
        context: Context ("ask" ou "mention")
        user_name: Nom de l'utilisateur
        game_cache: Cache des jeux (optionnel pour enrichissement contexte)
    
    Returns:
        str: Réponse formatée (tronquée si nécessaire) ou None si erreur

```

#### enrich_prompt_with_game_context (func)

**Original doc**: 12 lines, 0 quantum terms


```text


    SMART CONTEXT 2.0: Auto-enrichissement révolutionnaire !
    NOUVELLE LOGIQUE: Si jeu détecté dans prompt → enrichir automatiquement
    Plus besoin de keywords - détection basée sur contenu réel !
    
    Args:
        prompt: Question originale de l'user
        game_cache: Instance GameCache
    
    Returns:
        str: Prompt enrichi ou prompt original si aucun jeu détecté

```

#### find_game_in_cache (func)

**Original doc**: 11 lines, 0 quantum terms


```text


    Trouve un jeu dans le cache en utilisant fuzzy matching.
    
    Args:
        user_query: Texte de l'utilisateur (ex: "brottato", "parle moi de brotato")
        game_cache: Instance GameCache
        threshold: Seuil de similarité (80% par défaut)
    
    Returns:
        dict: Données du jeu si trouvé, None sinon

```

### Standard Components

#### extract_mention_message (func)

```text


    Extrait le message d'une mention @bot ou bot_name.
    
    Args:
        message_content: Contenu complet du message "@bot <message>" ou "bot_name <message>"
        bot_name: Nom du bot (case-insensitive)
    
    Returns:
        str: Message extrait ou None si invalide

```

#### extract_question_from_command (func)

```text


    Extrait la question d'une commande !ask.
    
    Args:
        message_content: Contenu complet du message "!ask <question>"
    
    Returns:
        str: Question extraite ou None si invalide

```
