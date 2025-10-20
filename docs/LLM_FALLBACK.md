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

### 2. Système de fallback en cascade (NEW!)

**3 niveaux de fallback automatiques** :

```
Commande !ask
      ↓
┌─────────────────────┐
│ 1️⃣ LM Studio (local)│
└──────────┬──────────┘
           │ ❌ Timeout/Error
           ↓
┌─────────────────────┐
│ 2️⃣ OpenAI API       │
└──────────┬──────────┘
           │ ❌ No API key / Error
           ↓
┌─────────────────────┐
│ 3️⃣ Répliques fun    │  ← TOUJOURS disponible
└─────────────────────┘
```

**Code interne** (`call_model()`) :
```python
# Niveau 1 : Essayer LM Studio
result = await try_endpoint(api_url, ...)
if result:
    return result  # ✅ Succès

# Niveau 2 : Essayer OpenAI
result = await try_openai_fallback(...)
if result:
    return result  # ✅ Succès

# Niveau 3 : Retourner None
return None  # ❌ Tous échoués → commandes utilisent fallback répliques
```

**Avantages** :
- ✅ **Robustesse maximale** : 3 niveaux de sécurité
- ✅ **Coût optimisé** : OpenAI seulement si LM Studio fail
- ✅ **Expérience cohérente** : Bot toujours réactif
- ✅ **Production-ready** : Crash LM Studio = 0 downtime

### 3. Système de réponses fallback

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
- `"ask_error"` : Erreur LLM (3 variantes) ← **Utilisé quand tous les LLM échouent**

### 3. Intégration dans les commandes

Les commandes `!ask` et `!chill` gèrent automatiquement le fallback en cascade :

```python
async def handle_ask_command(..., llm_available: bool = True):
    # Boot detection : Si LLM marqué indisponible au démarrage → fallback immédiat
    if not llm_available:
        fallback_msg = get_fallback_response("ask")
        await message.channel.send(f"@{user} {fallback_msg}")
        return
    
    # Runtime cascade : Essayer LM Studio → OpenAI → Fallback répliques
    response = await call_model(prompt, config, user=user, mode="ask")
    
    # Si tous les LLM ont échoué (retourne None) → fallback répliques
    if response is None:
        fallback_msg = get_fallback_response("ask_error")
        await message.channel.send(f"@{user} {fallback_msg}")
        return
    
    # Sinon → utiliser la réponse LLM normale
    await message.channel.send(f"@{user} {response}")
```

**Double sécurité** :
- ✅ **Boot detection** : Si aucun LLM au démarrage → skip appel réseau
- ✅ **Runtime cascade** : Si crash post-boot → fallback automatique

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
│ Cascade  │ │ Fallback │
│ LM→OpenAI│ │ direct   │
└────┬─────┘ └────┬─────┘
     │            │
     ▼            ▼
 ┌───────┐   ┌──────────┐
 │LLM OK?│   │ Réplique │
 └───┬───┘   │   fun    │
     │       └──────────┘
 ┌───┴───┐
 │Fail?  │
 └───┬───┘
     │
     ▼
 ┌──────────┐
 │ Réplique │
 │   fun    │
 └──────────┘
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

### Le bot crashe si LM Studio tombe en plein live

**Réponse** : ✅ **Non, il ne crashe pas !** Avec le système de cascade :

```
1. User: !ask Question
2. Bot essaie LM Studio → timeout (10s max)
3. Bot essaie OpenAI → fail (pas de clé)
4. Bot envoie réplique fallback → "💀 Mes neurones bugguent, réessaie dans 2 min !"
```

**Résultat** : 0 downtime, expérience cohérente ! 🎯

### Les tests LLM échouent en local

**Cause** : LM Studio non lancé.

**Solution** :
```bash
# Option 1 : Lance LM Studio
# Option 2 : Skip les tests LLM
pytest tests/ -m "not llm"
```

### Comment savoir quel niveau de fallback a été utilisé ?

**Logs** :
```
[MODEL] 🔗 Tentative LM Studio...
[MODEL] ❌ LM_STUDIO failed: timeout
[MODEL] 🌐 Utilisation du fallback OpenAI (si configuré)
[MODEL] ⚠️ Pas de clé OpenAI configurée
[ASK] 🤖 Tous LLM indisponibles → fallback répliques
[ASK] ✅ Fallback error envoyé: 💀 Mes neurones bugguent...
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

**Q: Que se passe-t-il si LM Studio crash pendant un live ?**  
R: Cascade automatique : LM Studio (fail) → OpenAI (si configuré) → Répliques fun. **0 downtime** ! 🎯

**Q: Combien coûte l'utilisation d'OpenAI en fallback ?**  
R: Seulement si LM Studio échoue. Avec `gpt-4o-mini` : ~0.0001$ par réponse (négligeable).

**Q: Peut-on désactiver OpenAI et garder seulement LM Studio + Répliques ?**  
R: Oui ! Laisse la section `openai` vide dans `config.yaml` → cascade LM Studio → Répliques directement.

---

## 🎖️ Crédits

Système conçu pour garantir une expérience utilisateur cohérente, que le bot ait accès à un LLM ou non.

**Philosophie** : Un bon bot Twitch doit **toujours répondre**, jamais rester silencieux. 🎯
