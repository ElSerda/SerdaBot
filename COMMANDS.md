# 📜 Liste des Commandes SerdaBot

## 🎮 Commandes Publiques

### `!ask <question>`
Pose une question à l'IA du bot.
- **Exemple** : `!ask Quel est le meilleur jeu de 2024 ?`
- **Cooldown** : 60 secondes par utilisateur
- **Activée si** : `ask` dans la config

### `!gameinfo <nom_du_jeu>`
Récupère les informations d'un jeu (via IGDB/RAWG).
- **Exemple** : `!gameinfo Elden Ring`
- **Cooldown** : 60 secondes par utilisateur
- **Activée si** : `game` dans la config

### `!donationserda` / `!serdakofi`
Affiche les liens de donation/support pour El_Serda.
- **Cooldown** : 60 secondes par utilisateur
- **Toujours activée**

### Mention du bot (Mode Chill)
Mentionne `@serda_bot` dans un message pour obtenir une réponse sarcastique à la El_Serda.
- **Exemple** : `@serda_bot tu penses quoi de ce jeu ?`
- **Cooldown** : 60 secondes par utilisateur
- **Activée si** : `chill` dans la config

---

## 🛡️ Commandes Modérateur (MOD Only)

### 📝 Gestion des Devs (Whitelist Traduction Auto)

#### `!adddev @username`
Ajoute un utilisateur à la whitelist de traduction automatique.
- Les messages de ce dev seront automatiquement traduits EN→FR
- **Exemple** : `!adddev @john_dev`

#### `!removedev @username` / `!deldev @username`
Retire un utilisateur de la whitelist de traduction.
- **Exemple** : `!deldev @john_dev`

#### `!listdevs`
Affiche la liste complète des devs whitelistés pour la traduction.
- **Exemple de sortie** : `📋 Devs whitelistés (3): @alice, @bob, @charlie`

---

### 🚫 Gestion des Sites Bloqués (Anti-Spam)

#### `!blocksite <nom_site>`
Ajoute un site/mot-clé à la blacklist anti-spam.
- Les bots contenant ce mot dans leur nom ou message seront automatiquement timeout (60s)
- **Exemple** : `!blocksite streamboo`
- **Exemple** : `!blocksite primes4free`

#### `!unblocksite <nom_site>`
Retire un site de la blacklist.
- **Exemple** : `!unblocksite streamboo`

#### `!blockedlist`
Affiche tous les sites/mots-clés bloqués.
- **Exemple de sortie** : `🚫 Sites bloqués (5): primes4free, streamboo, fakeviews, ...`

---

### 🤖 Gestion des Bots (Whitelist/Blacklist)

#### `!addwhitebot @bot_name`
Ajoute un bot à la whitelist.
- **Effet** : SerdaBot ne répondra **jamais** à ce bot (aucune commande, aucune réaction)
- **Utilité** : Éviter les interactions bot-to-bot inutiles
- **Exemple** : `!addwhitebot @nightbot`

#### `!delwhitebot @bot_name`
Retire un bot de la whitelist.
- **Exemple** : `!delwhitebot @nightbot`

#### `!addblackbot @bot_name`
Ajoute un bot à la blacklist.
- **Effet** : SerdaBot ignorera **complètement** tous les messages de ce bot
- **Différence avec whitelist** : Plus strict, aucun traitement du message
- **Exemple** : `!addblackbot @spam_bot`

#### `!delblackbot @bot_name`
Retire un bot de la blacklist.
- **Exemple** : `!delblackbot @spam_bot`

#### `!whitebots`
Affiche tous les bots dans la whitelist.
- **Exemple de sortie** : `📋 Bots whitelistés (2): @nightbot, @streamelements`

#### `!blackbots`
Affiche tous les bots dans la blacklist.
- **Exemple de sortie** : `🚫 Bots blacklistés (1): @spam_bot`

---

### 🌐 Traduction Manuelle

#### `!translate <texte>` / `!trad <texte>`
Traduit manuellement un texte (détection automatique FR↔EN).
- **Auto-détection** : Si le texte contient des mots français (le, la, les, de, du, un, une) → FR→EN, sinon → EN→FR
- **Exemple** : `!trad This is a test` → 🇬🇧 This is a test / 🇫🇷 C'est un test
- **Exemple** : `!trad Ceci est un test` → 🇫🇷 Ceci est un test / 🇬🇧 This is a test

---

## ⚙️ Configuration

### Cooldown Global
Par défaut : **60 secondes** entre chaque commande par utilisateur.
- Configurable dans `config.yaml` : `bot.cooldown`

### Commandes Activées
Les commandes peuvent être activées/désactivées dans `config.yaml` :
```yaml
bot:
  enabled_commands:
    - ask      # Active !ask
    - game     # Active !gameinfo
    - chill    # Active les mentions du bot
```

### Traduction Automatique
Activée/désactivée dans `config.yaml` :
```yaml
bot:
  auto_translate: true  # Active la traduction auto pour les devs whitelistés
```

---

## 📊 Résumé

| Type | Nombre de commandes |
|------|---------------------|
| **Publiques** | 4 |
| **Modérateur** | 15 |
| **TOTAL** | **19 commandes** |

---

## 🗂️ Fichiers de Données

Les listes sont sauvegardées dans `data/` :
- `devs.json` - Whitelist devs pour traduction auto
- `blocked_sites.json` - Sites/mots-clés bloqués (anti-spam)
- `bot_whitelist.json` - Bots à ne pas répondre
- `bot_blacklist.json` - Bots à ignorer complètement

---

*Dernière mise à jour : 16 octobre 2025*
