# 🎮 Guide d'Intégration - Nouvelles Commandes

**Date:** 2025-10-20  
**Commandes:** `!prix` et `!temps`

## 📋 Fichiers Créés

```
src/core/commands/
├── api/
│   ├── cheapshark.py .......... API CheapShark (prix)
│   └── hltb.py ................ API HowLongToBeat (durée)
├── prix_command.py ............ Handler !prix
└── temps_command.py ........... Handler !temps
```

---

## 🚀 Intégration dans `twitch_bot.py`

### Étape 1: Ajouter les imports

```python
# Dans twitch_bot.py, ajouter après les autres imports de commandes:
from core.commands.prix_command import handle_prix_command
from core.commands.temps_command import handle_temps_command
```

### Étape 2: Ajouter la détection dans `on_message()`

```python
# Dans la fonction on_message(), après la détection de !gameinfo:

# Commande !prix
if cleaned.startswith("!prix ") and "game" in self.enabled:
    game_name = cleaned[6:].strip()
    now = time.time()
    
    if user in user_last_command:
        if now - user_last_command[user] < cooldown:
            if self.config["bot"].get("debug", False):
                print(f"[COOLDOWN] User {user} en cooldown pour !prix")
            return
    
    user_last_command[user] = now
    await handle_prix_command(message, self.config, game_name, now)
    return

# Commande !temps
if cleaned.startswith("!temps ") and "game" in self.enabled:
    game_name = cleaned[7:].strip()
    now = time.time()
    
    if user in user_last_command:
        if now - user_last_command[user] < cooldown:
            if self.config["bot"].get("debug", False):
                print(f"[COOLDOWN] User {user} en cooldown pour !temps")
            return
    
    user_last_command[user] = now
    await handle_temps_command(message, self.config, game_name, now)
    return
```

---

## 📦 Installation des Dépendances

### Pour !temps (HowLongToBeat)

```bash
# Obligatoire pour !temps
pip install howlongtobeatpy
```

### Pour !prix (CheapShark)

✅ Aucune dépendance requise (API publique)

---

## 🧪 Tests

### Test Rapide

```bash
# Dans votre environnement de dev
python -c "
import asyncio
from core.commands.api import fetch_game_price, fetch_game_playtime

async def test():
    # Test CheapShark
    prix = await fetch_game_price('Hades')
    print(f'Prix: {prix}')
    
    # Test HowLongToBeat
    temps = await fetch_game_playtime('Hades')
    print(f'Temps: {temps}')

asyncio.run(test())
"
```

### Test en Live

1. Lancer le bot
2. Dans le chat Twitch:
   - `!prix Hades`
   - `!temps Hades`
   - `!gameinfo Hades` (vérifier que ça marche toujours)

---

## 📝 Configuration (Optionnel)

Aucune configuration supplémentaire requise ! Les commandes utilisent la config existante (`cooldown`, `debug`, etc.).

---

## 🎯 Exemples de Réponses

### !prix Hades
```
@user 💰 Hades: 20,99€ sur Steam (-15%) (https://cheapshark.com/...) (60s)
```

### !temps Hades
```
@user ⏱️ Hades: 22h (histoire) | 95h (100%) (60s)
```

### !gameinfo Hades
```
@user 🎮 Hades (2020), PC, PS5, Xbox
⭐ Metacritic: 93/100 | Note: 4.3/5 (15k avis) :
Un rogue-like où tu incarnes Zagreus... (lien) (60s)
```

---

## ⚡ Améliorations Futures (Optionnel)

### Option 1: Intégrer le prix dans !gameinfo

```python
# Dans game_command.py, après la récupération des données:
if 'PC' in platforms:
    price_data = await fetch_game_price(game_name)
    if price_data:
        rating_line += f"\n💰 {price_data['price']} sur {price_data['store']}"
```

### Option 2: Alias de commandes

```python
# Dans twitch_bot.py:
if cleaned.startswith("!price "):  # Alias anglais
    # Même traitement que !prix
```

### Option 3: Commande combinée

```python
# !jeu Hades → Tout en un (!gameinfo + !prix + !temps)
```

---

## 🐛 Troubleshooting

### Erreur: `howlongtobeatpy` not found
**Solution:** `pip install howlongtobeatpy`

### !temps ne retourne rien
**Cause:** Jeu pas dans la base HowLongToBeat  
**Solution:** Normal, tous les jeux ne sont pas référencés

### !prix affiche toujours "Steam"
**Cause:** Mapping des stores pas implémenté  
**Solution:** Voir TODO dans `cheapshark.py` ligne 95

---

## ✅ Checklist d'Intégration

- [ ] Ajouter imports dans `twitch_bot.py`
- [ ] Ajouter détection de `!prix` dans `on_message()`
- [ ] Ajouter détection de `!temps` dans `on_message()`
- [ ] Installer `howlongtobeatpy` (pour !temps)
- [ ] Tester `!prix Hades`
- [ ] Tester `!temps Hades`
- [ ] Vérifier que `!gameinfo` marche toujours
- [ ] Mettre à jour `COMMANDS.md` (documentation)

---

## 📚 Documentation

**Voir aussi:**
- `TODO-DEV/REFONTE_GAMEINFO_RECAP.md` - Documentation complète
- `TODO-DEV/game-search.md` - TODO originale
- `src/core/commands/api/` - Code source des APIs

---

**Status:** ✅ Prêt à intégrer  
**Temps estimé:** 10 minutes  
**Complexité:** Facile
