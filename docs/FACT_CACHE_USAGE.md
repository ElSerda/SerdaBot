# Fact Cache - Guide d'Utilisation

## 🎯 Objectif

Le Fact Cache réduit les hallucinations du modèle 1.5B en fournissant des réponses vérifiées depuis Wikipedia avant d'interroger le modèle local.

---

## 🚀 Utilisation

### Mode Automatique (Wikipedia)

Lorsqu'un utilisateur pose une question factuelle avec `!ask`, le bot :

1. **Normalise la query** : "c'est quoi les pandas roux ?" → "pandas roux"
2. **Cherche dans le cache** en mémoire (instantané)
3. **Si pas trouvé** : appel Wikipedia API
4. **Si trouvé** : ajoute au cache et répond directement
5. **Si Wikipedia fail** : appel modèle 1.5B (dernier recours)

**Exemple** :
```
User: !ask c'est quoi un axolotl
Bot: [WIKI] 🔍 Recherche: axolotl
Bot: [WIKI] ✅ Ajouté au cache: axolotl
Bot: @user L'axolotl est une salamandre aquatique originaire du lac Xochimilco...
```

---

## 🔧 Commandes Admin

### !cacheadd <query> | <answer>
Ajoute manuellement un fait au cache.

**Usage** :
```
!cacheadd panda roux | Petit mammifère arboricole d'Asie, roux et blanc, menacé d'extinction. Famille des Ailuridae.
```

**Restrictions** :
- Réservé aux devs listés dans `config/config.json` → `bot.devs`
- Réponse doit faire >30 chars
- Ne doit pas contenir "Je ne sais pas"

---

### !cachestats
Affiche les statistiques du cache.

**Usage** :
```
!cachestats
```

**Output** :
```
@user 📊 Cache: 42 faits | cache/dynamic_facts.json
```

---

### !cacheclear
Vide complètement le cache (DANGER).

**Usage** :
```
!cacheclear
```

**Output** :
```
@user 🗑️ Cache vidé complètement.
```

⚠️ **Attention** : Cette action est irréversible !

---

## 📁 Structure Fichiers

```
SerdaBot/
├── cache/
│   └── dynamic_facts.json   ← Cache persistant (auto-sauvegardé)
├── src/
│   ├── utils/
│   │   └── cache_manager.py ← Logique cache + Wikipedia
│   └── core/
│       └── commands/
│           ├── ask_command.py      ← Intégration cache dans !ask
│           └── cache_commands.py   ← Commandes admin
```

---

## 🔍 Format Cache

`cache/dynamic_facts.json` :
```json
{
  "pandas roux": "Petit mammifère arboricole d'Asie, roux et blanc...",
  "python": "Langage de programmation polyvalent et simple...",
  "axolotl": "L'axolotl est une salamandre aquatique originaire..."
}
```

**Keys normalisées** :
- Minuscule
- Sans `?`, `!`, `.`
- Préfixes retirés : "c'est quoi", "explique", "parle moi de"

---

## ⚙️ Configuration

### Rate Limit Wikipedia
`src/utils/cache_manager.py` :
```python
_WIKI_RATE_LIMIT = 1.0  # 1 requête/sec
```

**Respect des limites** :
- Wikipedia API : 200 req/s max (on utilise 1/s pour être safe)
- Cache agressif pour minimiser les calls

### Détection Question Factuelle

**Patterns inclus** :
```python
["quoi", "quest", "explique", "parle", "comment", "pourquoi", "?"]
```

**Patterns exclus (CHILL)** :
```python
["salut", "hello", "yo", "gg", "lol", "comment ça va"]
```

---

## 📊 Métriques

### Performance Attendue

| Métrique | Valeur Cible |
|----------|--------------|
| **Hit rate cache** | >70% sur queries répétées |
| **Latency cache hit** | <1ms |
| **Latency cache miss + Wikipedia** | <500ms |
| **Réduction hallucinations** | -80% sur sujets encyclopédiques |

### Monitoring

Logs produits :
```
[CACHE] ✅ 42 faits chargés depuis cache/dynamic_facts.json
[CACHE] 💡 Hit: pandas roux
[WIKI] 🔍 Recherche: axolotl
[WIKI] ✅ Ajouté au cache: axolotl
[CACHE] ➕ Ajout manuel: python
```

---

## 🐛 Troubleshooting

### Cache ne se charge pas
```bash
# Vérifier le fichier existe
ls -lh cache/dynamic_facts.json

# Vérifier JSON valide
python -m json.tool cache/dynamic_facts.json
```

### Wikipedia API échoue
- Vérifier connexion internet
- Rate limit dépassé ? Attendre 1 sec
- Titre inexact ? Le bot normalise automatiquement

### Réponse trop longue (>230 chars)
Le bot tronque automatiquement à 230 chars à la dernière ponctuation.

---

## 🚀 Enregistrement Commandes (bot.py)

Ajouter dans `src/bot.py` :

```python
from core.commands.cache_commands import (
    handle_cacheadd_command,
    handle_cachestats_command,
    handle_cacheclear_command
)

# Dans event_message
if content.startswith("!cacheadd "):
    args = content[10:].strip()
    await handle_cacheadd_command(message, self.config, args)

elif content == "!cachestats":
    await handle_cachestats_command(message, self.config)

elif content == "!cacheclear":
    await handle_cacheclear_command(message, self.config)
```

---

## 📈 Exemples d'Utilisation

### Scénario 1 : Première question
```
User: !ask c'est quoi un SSD
Bot: [WIKI] 🔍 Recherche: ssd
Bot: [WIKI] ✅ Ajouté au cache: ssd
Bot: @user Un SSD est un périphérique de stockage de données utilisant de la mémoire flash...
```

### Scénario 2 : Question répétée
```
User: !ask c'est quoi un SSD
Bot: [CACHE] 💡 Hit: ssd
Bot: @user Un SSD est un périphérique de stockage de données utilisant de la mémoire flash...
```
**Latence : <1ms** au lieu de ~500ms !

### Scénario 3 : Ajout manuel admin
```
Dev: !cacheadd valorant | Jeu de tir tactique 5v5 développé par Riot Games, sorti en 2020.
Bot: @dev ✅ Ajouté au cache: 'valorant...'

User: !ask c'est quoi valorant
Bot: [CACHE] 💡 Hit: valorant
Bot: @user Jeu de tir tactique 5v5 développé par Riot Games, sorti en 2020.
```

---

## ✅ Checklist Déploiement

- [ ] `cache/` directory créé
- [ ] `cache_manager.py` importé au démarrage
- [ ] `ask_command.py` intègre `get_cached_or_fetch()`
- [ ] Commandes admin enregistrées dans `bot.py`
- [ ] Devs listés dans `config.json` → `bot.devs`
- [ ] Test `!ask c'est quoi python` → vérifie logs Wikipedia
- [ ] Test `!cacheadd` avec compte dev
- [ ] Test `!cachestats`

---

## 🎯 Résultat Attendu

**Avant (sans cache)** :
```
User: !ask c'est quoi un panda roux
Bot: @user Les pandas roux sont des louveteaux de la famille des bearacées.
```
❌ **Hallucination totale !**

**Après (avec cache Wikipedia)** :
```
User: !ask c'est quoi un panda roux
Bot: @user Le petit panda est un mammifère, seul représentant du genre Ailurus...
```
✅ **Réponse vérifiée depuis Wikipedia !**
