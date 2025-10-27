# commands.translation

**Migré depuis**: `commands/translation.py`  
**Lignes doc originales**: 13  
**Éléments over-engineered**: 0  

---

## Module Overview

```text


Translation Commands - !trad 
Système de traduction multilingue avec Google API

```

## API Reference

### Standard Components

#### TranslationCommands (class)

```text

Commandes de traduction.

```

#### _is_broadcaster_or_mod (func)

```text

Vérifie si l'utilisateur est broadcaster ou modérateur.

```

#### _load_devs_whitelist (func)

```text

Charge la whitelist des devs depuis JSON.

```

#### _save_devs_whitelist (func)

```text

Sauvegarde la whitelist des devs en JSON.

```

#### add_dev (func)

```text

Ajoute un dev à la whitelist auto-translate.

```

#### del_dev (func)

```text

Retire un dev de la whitelist auto-translate.

```

#### list_devs (func)

```text

Affiche la liste des devs en whitelist.

```

#### prepare (func)

```text

Setup function for TwitchIO.

```

#### translate_text (func)

```text

Traduit n'importe quelle langue → français (config).

```
