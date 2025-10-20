# 🤖 Système de Fallback LLM

Ce document explique comment SerdaBot gère l'absence de LLM local et garantit une expérience utilisateur cohérente.

---

## 🎯 Philosophie

**Problème** : Un LLM local (LM Studio) n'est pas toujours disponible :
- ⚠️ En CI (GitHub Actions) → pas de GPU, pas de LM Studio
- ⚠️ Sur un fork → utilisateur sans LLM installé
- ⚠️ En production → LM Studio peut crasher temporairement

**Solution** : Système de fallback automatique avec réponses pré-définies.

**Résultat** :
- ✅ Bot **toujours fonctionnel** (avec ou sans LLM)
- ✅ Tests CI **100% verts** (pas de dépendance au LLM)
- ✅ Fork **immédiatement utilisable** (pas besoin de GPU)
- ✅ Production **robuste** (pas de freeze si LLM down)

---

## 🏗️ Architecture

### 1. Détection au démarrage

Au lancement du bot, `TwitchBot.__init__()` vérifie automatiquement la disponibilité du LLM :

```python
from src.utils.llm_detector import check_llm_status, get_llm_mode

# Détection du LLM
llm_mode = get_llm_mode(self.config)

if llm_mode == "auto":
    self.llm_available, status_msg = check_llm_status(self.config)
    print(status_msg)
    # → "✅ LLM détecté : http://localhost:1234/v1"
    # → "⚠️  LLM non disponible → mode fallback activé"
```

**Avantages** :
- ✅ Vérification **une seule fois** au boot (pas à chaque commande)
- ✅ **0 latence** sur les commandes (décision déjà prise)
- ✅ Détection **silencieuse** (pas de spam réseau)

### 2. Système de réponses fallback

Quand le LLM n'est pas disponible, `src/core/fallbacks.py` fournit des réponses pré-définies :

```python
from src.core.fallbacks import get_fallback_response

# Réponse pour !ask
response = get_fallback_response("ask")
# → "Je réfléchis… mais mon cerveau est en pause 🧠💤"

# Réponse pour @mention
response = get_fallback_response("chill")
# → "Salut ! 👋"
```

**Intentions disponibles** :
- `"ask"` : Réponses pour `!ask` (8 variantes)
- `"chill"` : Réponses pour `@mention` (19 variantes)
- `"ask_timeout"` : Timeout LLM (4 variantes)
- `"ask_error"` : Erreur LLM (3 variantes)

### 3. Intégration dans les commandes

Les commandes `!ask` et `!chill` vérifient automatiquement `llm_available` :

```python
async def handle_ask_command(..., llm_available: bool = True):
    # Si LLM indisponible → fallback immédiat
    if not llm_available:
        fallback_msg = get_fallback_response("ask")
        await message.channel.send(f"@{user} {fallback_msg}")
        return
    
    # Sinon → logique LLM normale
    response = await call_model(...)
```

---

## 🔧 Configuration

### Mode automatique (par défaut)

```yaml
# Pas de config nécessaire → auto-détection
```

Le bot détecte automatiquement si LM Studio est accessible.

### Mode manuel (optionnel)

Tu peux forcer l'activation/désactivation via variable d'environnement :

```bash
# Forcer l'utilisation du LLM (même si non détecté)
export LLM_MODE=enabled
./start_bot.sh

# Forcer le mode fallback (même si LLM disponible)
export LLM_MODE=disabled
./start_bot.sh

# Auto-détection (défaut)
export LLM_MODE=auto
./start_bot.sh
```

Ou via config (future feature) :

```yaml
bot:
  llm:
    enabled: auto  # auto | true | false
    endpoint: "http://localhost:1234/v1"
    fallback_mode: "fun"  # fun | silent | minimal
```

**Modes fallback** :
- `fun` : Répliques humoristiques (défaut)
- `silent` : Message neutre ("Commande temporairement indisponible.")
- `minimal` : Juste un emoji ("🤖")

---

## 🧪 Tests

### Tests avec LLM (marqués `@pytest.mark.llm`)

Ces tests **nécessitent LM Studio** et sont **skippés en CI** :

```python
import pytest

@pytest.mark.llm
@pytest.mark.asyncio
async def test_ask_with_real_llm():
    """Teste que le LLM répond correctement (nécessite LM Studio)."""
    response = await call_model("C'est quoi Python ?", config, mode='ask')
    assert "langage" in response.lower()
```

### Tests sans LLM (toujours exécutés)

Ces tests vérifient le **fallback** et passent **toujours** :

```python
async def test_ask_fallback_when_no_llm():
    """Teste le fallback quand LLM indisponible."""
    response = get_fallback_response("ask")
    assert len(response) > 5
    assert len(response) < 200
```

### Lancer les tests

```bash
# Par défaut : skip les tests LLM
pytest tests/

# Lancer TOUS les tests (y compris LLM)
pytest tests/ -m ""

# Lancer UNIQUEMENT les tests LLM
pytest tests/ -m "llm"

# Lancer tout SAUF les tests LLM
pytest tests/ -m "not llm"
```

---

## 📊 Flux de décision

```
┌─────────────────────────┐
│   Bot démarre           │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Détection LLM           │
│ (llm_detector.py)       │
└───────────┬─────────────┘
            │
      ┌─────┴─────┐
      │           │
      ▼           ▼
 ┌────────┐  ┌────────┐
 │ LLM OK │  │ Pas de │
 │        │  │  LLM   │
 └────┬───┘  └───┬────┘
      │          │
      │          │
      ▼          ▼
┌──────────┐ ┌──────────┐
│ Commande │ │ Commande │
│ !ask     │ │ !ask     │
└────┬─────┘ └────┬─────┘
     │            │
     ▼            ▼
┌──────────┐ ┌──────────┐
│ Appel    │ │ Fallback │
│ LLM      │ │ pré-def  │
└──────────┘ └──────────┘
```

---

## 🎨 Personnalisation des réponses

### Ajouter des réponses custom

```python
from src.core.fallbacks import add_custom_fallback

# Ajouter des réponses pour une nouvelle intention
add_custom_fallback("greetings", [
    "Coucou ! 👋",
    "Salut la compagnie !",
    "Bien ou bien ? 😎"
])

# Utiliser
response = get_fallback_response("greetings")
```

### Modifier les réponses existantes

Édite `src/core/fallbacks.py` :

```python
FALLBACKS = {
    "ask": [
        "Ton message custom ici 🤖",
        # ... autres réponses
    ],
    "chill": [
        "Ta salutation custom ! 👋",
        # ... autres réponses
    ],
}
```

---

## 🚀 Pour les contributeurs

### Ajouter un nouveau fallback

1. **Ajoute l'intention dans `fallbacks.py`** :

```python
FALLBACKS = {
    # ... intentions existantes
    "nouvelle_intention": [
        "Réponse 1",
        "Réponse 2",
        "Réponse 3",
    ],
}
```

2. **Utilise dans ta commande** :

```python
if not llm_available:
    response = get_fallback_response("nouvelle_intention")
    await message.channel.send(response)
    return
```

3. **Ajoute des tests** :

```python
def test_nouvelle_intention():
    response = get_fallback_response("nouvelle_intention")
    assert isinstance(response, str)
    assert len(response) > 0
```

### Guidelines

- ✅ Réponses **courtes** (< 200 chars)
- ✅ Ton **cohérent** avec le bot (geek, fun, second degré)
- ✅ Plusieurs **variantes** (éviter la répétition)
- ✅ **Twitch-safe** (< 500 chars absolument)

---

## 🐛 Troubleshooting

### Le bot utilise toujours le fallback (alors que LLM est dispo)

**Cause** : LM Studio non détecté au démarrage.

**Solution** :
```bash
# Vérifie que LM Studio est bien lancé
curl http://localhost:1234/v1/models

# Si erreur → lance LM Studio
# Sinon → redémarre le bot
```

### Le bot utilise le LLM (alors que je veux le fallback)

**Solution** :
```bash
# Force le mode fallback
export LLM_MODE=disabled
./start_bot.sh
```

### Les tests LLM échouent en local

**Cause** : LM Studio non lancé.

**Solution** :
```bash
# Option 1 : Lance LM Studio
# Option 2 : Skip les tests LLM
pytest tests/ -m "not llm"
```

---

## 📚 Références

- **Code source** :
  - `src/utils/llm_detector.py` - Détection LLM
  - `src/core/fallbacks.py` - Réponses fallback
  - `src/chat/twitch_bot.py` - Intégration au bot

- **Tests** :
  - `tests/test_llm_fallback.py` - Tests du système fallback
  - `tests/test_pipeline_integration.py` - Tests marqués `@pytest.mark.llm`

- **Config** :
  - `pytest.ini` - Configuration markers pytest
  - `src/config/config.example.yaml` - Template de config

---

## ❓ FAQ

**Q: Le fallback ralentit-il les commandes ?**  
R: Non, la détection est faite **une seule fois au boot**. Sur les commandes, c'est juste un `if` → **0 latence**.

**Q: Peut-on utiliser le bot UNIQUEMENT en mode fallback ?**  
R: Oui ! `export LLM_MODE=disabled` → bot 100% fonctionnel sans LLM.

**Q: Les réponses fallback sont-elles toujours les mêmes ?**  
R: Non, elles sont **aléatoires** (choix random dans la liste).

**Q: Peut-on mélanger LLM + fallback ?**  
R: Oui ! Le bot peut passer de l'un à l'autre (ex: LLM crash en live → fallback immédiat).

**Q: Faut-il modifier le code pour ajouter des réponses ?**  
R: Non, utilise `add_custom_fallback()` en runtime ou édite `fallbacks.py`.

---

## 🎖️ Crédits

Système conçu pour garantir une expérience utilisateur cohérente, que le bot ait accès à un LLM ou non.

**Philosophie** : Un bon bot Twitch doit **toujours répondre**, jamais rester silencieux. 🎯
