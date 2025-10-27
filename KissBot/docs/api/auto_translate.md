# intelligence.auto_translate

**Migré depuis**: `intelligence/auto_translate.py`  
**Lignes doc originales**: 9  
**Éléments over-engineered**: 0  

---

## Module Overview

```text


Auto-translate Events - Devs Whitelist Integration
Gestion des messages auto-traduits pour devs whitelistés

```

## API Reference

### Standard Components

#### AutoTranslateHandler (class)

```text

Gestionnaire auto-traduction devs whitelist.

```

#### _is_dev_whitelisted (func)

```text

Vérifie si user est dans whitelist devs.

```

#### _is_french_message (func)

```text

Détection simple si un message est en français.

```

#### _load_devs_whitelist (func)

```text

Charge la whitelist des devs depuis JSON.

```

#### handle_message (func)

```text

Traite un message pour auto-traduction si nécessaire.

```
