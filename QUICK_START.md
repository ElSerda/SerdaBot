# ⚡ KissBot V1 - Quick Start (5 minutes)

**Pour les impatients qui veulent un bot LIVE immédiatement !**

## 🚀 Installation Ultra-Rapide

```bash
# Une seule commande, tout s'installe !
curl -sSL https://raw.githubusercontent.com/ElSerda/SerdaBot/kissbot/quick-install.sh | bash
```

## ⚡ Configuration Express (5 minutes)

### 1. Token Twitch (2 min) - OBLIGATOIRE
```
1. Allez sur : https://twitchtokengenerator.com/
2. Cliquez "Bot Chat Token" 
3. Connectez-vous avec votre compte Twitch
4. Copiez le token (commence par oauth:)
```

### 2. App Twitch (2 min) - OBLIGATOIRE  
```
1. Allez sur : https://dev.twitch.tv/console/apps
2. "Register Your Application"
3. Name: "MonBot", OAuth: "http://localhost:3000", Category: "Chat Bot"
4. Notez Client ID et créez Client Secret
```

### 3. User ID (30 sec) - OBLIGATOIRE
```
1. Allez sur : https://www.streamweasels.com/twitch-tools/username-converter/
2. Entrez votre pseudo Twitch
3. Notez le User ID (nombre)
```

### 4. Config Minimum (30 sec)
```yaml
# Éditez config.yaml - MINIMUM VITAL :
bot:
  name: "votre_pseudo"

twitch:
  token: "oauth:VOTRE_TOKEN"
  client_id: "VOTRE_CLIENT_ID" 
  client_secret: "VOTRE_SECRET"
  bot_id: "VOTRE_USER_ID"
  channels: ["votre_pseudo"]
```

## 🎊 Lancement Immédiat

```bash
# Validation config
python3 validate_config.py

# Lancement bot
./start_kissbot.sh
```

**✅ Votre bot est LIVE ! Testez avec `!ping` dans votre chat Twitch**

---

## 🔥 Optimisations Optionnelles (après test)

### RAWG API - Commandes Jeux (GRATUIT)
- Site : https://rawg.io/apidocs
- Ajoute : `!gameinfo minecraft`, `!suggest`

### OpenAI API - LLM Fallback (PAYANT)  
- Site : https://platform.openai.com/
- Ajoute : Réponses IA de qualité supérieure

### LM Studio - LLM Local (GRATUIT)
- Site : https://lmstudio.ai/
- Ajoute : IA locale sans coût par token

---

**🎯 En 5 minutes : Bot fonctionnel**
**🚀 En 15 minutes : Bot complet avec toutes les features**

**Guide complet :** [COMPLETE_API_SETUP_GUIDE.md](COMPLETE_API_SETUP_GUIDE.md)