# 🛡️ Gestion AutoMod Twitch (TODO)

## 📋 Ce qui existe actuellement

Le bot a un **système anti-spam maison** qui timeout les users avec des mots-clés :
- ✅ Commandes : `!blocksite`, `!unblocksite`, `!blockedlist`
- ✅ Fichier : `data/blocked_sites.json`
- ✅ Action : `/timeout {user} 60` si message contient un mot bloqué

## 🚀 Ce qui pourrait être ajouté : AutoMod Twitch natif

### API Twitch pour AutoMod

Twitch propose plusieurs endpoints pour gérer l'AutoMod :

#### 1. **Blocked Terms (Ban Words)**
```
POST https://api.twitch.tv/helix/moderation/blocked_terms
```
Permet d'ajouter des mots bannis (comme l'interface Twitch)

#### 2. **AutoMod Settings**
```
PUT https://api.twitch.tv/helix/moderation/automod_settings
```
Configure le niveau d'AutoMod (0-4)

#### 3. **Check AutoMod Status**
```
POST https://api.twitch.tv/helix/moderation/enforcements/status
```
Vérifie si un message serait bloqué par AutoMod

---

## 🔧 Implémentation possible

### Nouvelles commandes MOD

```python
# Dans src/chat/twitch_bot.py

# Ajouter un mot banni via AutoMod Twitch
!addbanword <mot>
→ Ajoute "mot" à la liste des blocked_terms Twitch
→ Twitch bloquera automatiquement les messages avec ce mot

# Retirer un mot banni
!removebanword <mot>
→ Retire "mot" de la liste

# Voir les mots bannis
!banwords
→ Liste tous les blocked_terms actifs

# Configurer le niveau AutoMod
!automod <0-4>
→ 0 = Désactivé, 4 = Très strict
```

---

## 📝 Code à ajouter

### 1. Créer `src/utils/twitch_automod.py`

```python
import aiohttp
from typing import List, Optional

class TwitchAutoMod:
    """Gestion de l'AutoMod Twitch natif"""
    
    def __init__(self, client_id: str, access_token: str, broadcaster_id: str):
        self.client_id = client_id
        self.access_token = access_token
        self.broadcaster_id = broadcaster_id
        self.headers = {
            "Client-ID": client_id,
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    async def add_blocked_term(self, text: str) -> bool:
        """Ajoute un mot à la liste des blocked_terms Twitch"""
        url = "https://api.twitch.tv/helix/moderation/blocked_terms"
        data = {
            "broadcaster_id": self.broadcaster_id,
            "moderator_id": self.broadcaster_id,  # Ou l'ID du bot si MOD
            "text": text
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=data) as resp:
                return resp.status == 200
    
    async def remove_blocked_term(self, term_id: str) -> bool:
        """Retire un mot de la liste"""
        url = f"https://api.twitch.tv/helix/moderation/blocked_terms"
        params = {
            "broadcaster_id": self.broadcaster_id,
            "moderator_id": self.broadcaster_id,
            "id": term_id
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=self.headers, params=params) as resp:
                return resp.status == 204
    
    async def get_blocked_terms(self) -> List[dict]:
        """Récupère tous les mots bannis"""
        url = "https://api.twitch.tv/helix/moderation/blocked_terms"
        params = {
            "broadcaster_id": self.broadcaster_id,
            "moderator_id": self.broadcaster_id
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("data", [])
                return []
    
    async def set_automod_level(self, level: int) -> bool:
        """Configure le niveau AutoMod (0-4)"""
        url = "https://api.twitch.tv/helix/moderation/automod_settings"
        data = {
            "broadcaster_id": self.broadcaster_id,
            "moderator_id": self.broadcaster_id,
            "overall_level": level
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=self.headers, json=data) as resp:
                return resp.status == 200
```

### 2. Ajouter les commandes dans `twitch_bot.py`

```python
# Dans event_message, après les commandes existantes

elif cleaned.startswith("!addbanword") and is_mod:
    parts = content.split()
    if len(parts) > 1:
        word = parts[1]
        success = await self.automod.add_blocked_term(word)
        if success:
            await self.safe_send(
                message.channel,
                f"🚫 Mot '{word}' ajouté à l'AutoMod Twitch ! "
                f"Les messages avec ce mot seront bloqués."
            )
        else:
            await self.safe_send(message.channel, "❌ Erreur lors de l'ajout.")
    else:
        await self.safe_send(message.channel, f"@{user} Usage: !addbanword <mot>")
    return

elif cleaned.startswith("!banwords") and is_mod:
    terms = await self.automod.get_blocked_terms()
    if terms:
        words = [t["text"] for t in terms]
        await self.safe_send(
            message.channel,
            f"🚫 Mots bannis ({len(words)}): {', '.join(words)}"
        )
    else:
        await self.safe_send(message.channel, "ℹ️ Aucun mot banni.")
    return

elif cleaned.startswith("!automod") and is_mod:
    parts = content.split()
    if len(parts) > 1 and parts[1].isdigit():
        level = int(parts[1])
        if 0 <= level <= 4:
            success = await self.automod.set_automod_level(level)
            if success:
                await self.safe_send(
                    message.channel,
                    f"✅ AutoMod configuré au niveau {level}"
                )
            else:
                await self.safe_send(message.channel, "❌ Erreur de configuration.")
        else:
            await self.safe_send(message.channel, "⚠️ Niveau doit être 0-4")
    else:
        await self.safe_send(message.channel, f"@{user} Usage: !automod <0-4>")
    return
```

---

## ⚠️ Points importants

### 1. **Permissions requises**
Le token OAuth doit avoir ces scopes :
- `moderator:manage:blocked_terms`
- `moderator:manage:automod_settings`

### 2. **Bot doit être MOD**
Ces commandes ne fonctionnent que si le bot est MOD sur le canal.

### 3. **Différence avec le système actuel**

| Système | Action | Avantage |
|---------|--------|----------|
| **AutoMod Twitch** | Bloque le message AVANT qu'il apparaisse | Invisible pour le chat |
| **Bot actuel** | Timeout l'user APRÈS l'envoi | Message visible brièvement |

---

## 🚀 Prochaines étapes (si tu veux l'implémenter)

1. **Ajouter les scopes OAuth** dans l'authentification Twitch
2. **Créer `src/utils/twitch_automod.py`**
3. **Intégrer les commandes** dans `twitch_bot.py`
4. **Tester** sur ton canal d'abord

---

## 💡 Alternative simple

Si tu veux juste **consulter** les mots bannis sans API :
- L'interface Twitch : https://dashboard.twitch.tv/settings/moderation
- Mais pour les modifier en live via commandes, il faut passer par l'API

---

## 📊 Comparaison

**Système actuel** (blocksite) :
- ✅ Simple, déjà fonctionnel
- ✅ Timeout 60s (réversible)
- ❌ Message visible brièvement

**AutoMod Twitch** (à implémenter) :
- ✅ Bloque avant affichage (invisible)
- ✅ Intégré à Twitch (natif)
- ❌ Plus complexe à implémenter
- ❌ Nécessite scopes OAuth supplémentaires

---

**Veux-tu que j'implémente le système AutoMod Twitch natif ?** 🤔
