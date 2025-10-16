# 📖 Index de la Documentation SerdaBot

Bienvenue dans la documentation complète de SerdaBot !

---

## 🚀 Démarrage Rapide

- **[README.md](../README.md)** - Vue d'ensemble du projet
- **[INSTALL.md](../INSTALL.md)** - Instructions d'installation
- **[RELEASE_v0.1.0.md](../RELEASE_v0.1.0.md)** - Notes de version

---

## 📋 Documentation Principale

### Pour les Utilisateurs

- **[COMMANDS.md](./COMMANDS.md)** 📜  
  Liste complète des commandes et alias disponibles
  
- **[EASTER_EGG.md](./EASTER_EGG.md)** 🎉  
  Documentation du système d'easter egg (mode sarcastique El_Serda)

- **[TRANSLATION.md](./TRANSLATION.md)** 🌐  
  Système de traduction automatique pour devs anglophones

### Pour les Développeurs

- **[PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md)** 🗂️  
  Architecture du projet et organisation des fichiers
  
- **[PROMPTS.md](./PROMPTS.md)** 🎨  
  Guide complet pour créer et modifier les prompts
  
- **[TODO.md](./TODO.md)** 📋  
  Liste des tâches en cours et à venir

---

## 🎯 Guides par Objectif

### "Je veux utiliser le bot"
1. Lire [INSTALL.md](../INSTALL.md)
2. Lire [COMMANDS.md](./COMMANDS.md)
3. Configurer `config.yaml`
4. Lancer avec `tools/start_servers.sh`

### "Je veux personnaliser le comportement"
1. Lire [PROMPTS.md](./PROMPTS.md)
2. Éditer les fichiers dans `src/prompts/`
3. Tester en direct (pas besoin de redémarrer)

### "Je veux ajouter une commande"
1. Lire [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md)
2. Créer un fichier dans `src/core/commands/`
3. Ajouter l'alias dans `src/chat/twitch_bot.py`
4. Créer le prompt associé

### "Je veux comprendre l'easter egg"
1. Lire [EASTER_EGG.md](./EASTER_EGG.md)
2. Regarder `src/prompts/prompt_chill_elserda.txt`
3. Examiner `src/core/commands/chill_command.py`

### "Je veux contribuer au projet"
1. Lire [TODO.md](./TODO.md) pour voir les besoins
2. Fork le repo
3. Créer une branche feature
4. Soumettre une PR

---

## 🔧 Référence Technique

### Configuration
- **Fichier :** `src/config/config.yaml`
- **Template :** `config.sample.yaml`
- **Clés importantes :**
  - `bot.name` : Nom du bot Twitch
  - `bot.channel` : Canal à rejoindre
  - `bot.cooldown` : Délai entre commandes (secondes)
  - `bot.model_type` : Type de modèle (`openai` ou `ctransformers`)
  - `openai.api_key` : Clé API OpenAI
  - `openai.openai_model` : Modèle à utiliser (`gpt-3.5-turbo`, `gpt-4o-mini`)

### Structure des Fichiers
```
SerdaBot/
├── docs/                  # 📚 Documentation (vous êtes ici)
├── src/
│   ├── chat/             # 💬 TwitchIO bot
│   ├── config/           # ⚙️ Configuration YAML
│   ├── core/
│   │   ├── commands/     # 🎮 Handlers de commandes
│   │   └── server/       # 🌐 API FastAPI
│   ├── prompts/          # 🎨 Templates de prompts
│   └── utils/            # 🔧 Utilitaires
├── tools/                # 🛠️ Scripts de gestion
├── logs/                 # 📝 Logs d'exécution
└── db/sessions/          # 💾 Sessions (si applicable)
```

### Commandes Disponibles

| Commande | Aliases | Description | Accès |
|----------|---------|-------------|-------|
| `!game` | `!jeu`, `!gameinfo`, `!sb game` | Info sur un jeu vidéo | Tous |
| `!ask` | `!question`, `!sb ask` | Poser une question | Tous |
| `!translate` | `!trad`, `!sb translate` | Traduire FR↔EN | Mods |
| `!adddev` | - | Ajouter dev à whitelist | Mods |
| `!removedev` | - | Retirer dev de whitelist | Mods |
| `!listdevs` | - | Liste des devs whitelistés | Mods |
| Mention bot | `serda_bot salut` | Mode conversation | Tous |

---

## 🐛 Dépannage

### Le bot ne répond pas
1. Vérifier que le serveur API tourne (`tools/start_servers.sh`)
2. Vérifier les logs : `logs/api_server.log`
3. Vérifier le cooldown (10s par user)
4. Vérifier la connexion Twitch

### Les commandes ne marchent pas
1. Vérifier `enabled_commands` dans config
2. Tester les alias (ex: `!jeu` au lieu de `!game`)
3. Regarder les logs du terminal bot

### Le bot est trop lent
1. Vérifier la latence OpenAI
2. Considérer `gpt-3.5-turbo` si sur `gpt-4o-mini`
3. Réduire la longueur max des prompts

### Erreurs OpenAI
1. Vérifier la clé API dans `config.yaml`
2. Vérifier le quota/facturation sur platform.openai.com
3. Tester avec un autre modèle

---

## 📊 État du Projet

**Version actuelle :** v0.1.0  
**Statut :** ✅ Stable, en production  
**Modèle :** OpenAI GPT-3.5-turbo  
**Dernière mise à jour doc :** 15 octobre 2025

### Fonctionnalités
- ✅ Commandes multi-alias
- ✅ Easter egg El_Serda
- ✅ Info jeux (IGDB + Steam)
- ✅ Questions IA
- ✅ Traduction auto pour devs
- ⏳ Modèle local (futur)
- ⏳ Statistiques usage (futur)

---

## 🤝 Communauté

**Streamer :** El_Serda sur Twitch  
**Repo :** SerdaBot-test/SerdaBot  
**Licence :** AGPL-v3

**Contributions bienvenues !**

---

## 📝 Historique des Versions

### v0.1.0 (Octobre 2025)
- ✅ Release initiale
- ✅ Système d'alias
- ✅ Easter egg fonctionnel
- ✅ OpenAI integration
- ✅ Bot stable en prod

### v0.0.x (Développement)
- Prototypes initiaux
- Tests avec Mistral local
- Expérimentations

---

**Navigation :**
- 🏠 [Retour au README](../README.md)
- 📋 [Voir la TODO](./TODO.md)
- 🎨 [Guide Prompts](./PROMPTS.md)
- 📜 [Liste Commandes](./COMMANDS.md)
