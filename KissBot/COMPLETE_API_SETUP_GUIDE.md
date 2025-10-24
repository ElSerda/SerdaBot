# 🔑 KissBot V1 - Guide Complet APIs & Tokens

## 🎯 Vue d'ensemble : Ce dont vous avez besoin

| API/Service | Obligatoire ? | Utilisation | Coût |
|-------------|---------------|-------------|------|
| **Twitch Token** | ✅ **OUI** | Chat bot fonctionnel | **GRATUIT** |
| **Twitch App** | ✅ **OUI** | Client ID/Secret | **GRATUIT** |
| **RAWG API** | 🔶 Recommandé | Commandes jeux (!gameinfo) | **GRATUIT** |
| **OpenAI API** | 🔶 Optionnel | Fallback LLM si pas local | **PAYANT** |

---

## 🚀 PARTIE 1 : Configuration Twitch (OBLIGATOIRE)

### Étape 1A : Créer Application Twitch

1. **Allez sur** : https://dev.twitch.tv/console/apps
2. **Connectez-vous** avec votre compte Twitch principal
3. **Cliquez** "Register Your Application"
4. **Remplissez** :
   - **Name** : `KissBot-VotreNom` (ex: "KissBot-ElSerda")
   - **OAuth Redirect URLs** : `http://localhost:3000`
   - **Category** : `Chat Bot`
5. **Cliquez** "Create"
6. **NOTEZ** le **Client ID** affiché
7. **Cliquez** "New Secret" → **NOTEZ** le **Client Secret**

```yaml
# Dans config.yaml
twitch:
  client_id: "abc123def456..."      # ← Client ID
  client_secret: "xyz789uvw012..."  # ← Client Secret
```

### Étape 1B : Générer Token Bot

**🤖 MÉTHODE SIMPLE (Recommandée) :**

1. **Allez sur** : https://twitchtokengenerator.com/
2. **Sélectionnez** : "Bot Chat Token"
3. **Connectez-vous** avec le compte qui ENVERRA les messages :
   - **Option A** : Votre compte principal (bot parle avec votre nom)
   - **Option B** : Compte bot séparé (ex: "votrepseudo_bot")
4. **Autorisez** toutes les permissions demandées
5. **COPIEZ** le token généré (commence par `oauth:`)

**Scopes automatiquement inclus :**
- `chat:read` - Lire les messages du chat
- `chat:edit` - Envoyer des messages  
- `channel:moderate` - Actions de modération
- `whispers:read` - Lire les whispers
- `whispers:edit` - Envoyer des whispers

```yaml
# Dans config.yaml
twitch:
  token: "oauth:abc123def456..."  # ← Token généré
```

### Étape 1C : Récupérer User ID du Bot

1. **Allez sur** : https://www.streamweasels.com/twitch-tools/username-converter/
2. **Entrez** le nom du compte qui envoie les messages :
   - **Option A** : Votre pseudo principal
   - **Option B** : Pseudo du compte bot
3. **NOTEZ** le "User ID" (nombre, ex: "123456789")

```yaml
# Dans config.yaml
twitch:
  bot_id: "123456789"  # ← User ID numérique
```

### Étape 1D : Configuration finale Twitch

```yaml
# Dans config.yaml
bot:
  name: "nom_du_compte_qui_envoie"  # Votre pseudo OU pseudo du bot

twitch:
  token: "oauth:votre_token_ici"
  client_id: "votre_client_id"  
  client_secret: "votre_secret"
  bot_id: "votre_user_id_numerique"
  prefix: "!"
  channels: ["votre_channel_principal"]  # Channel à rejoindre
```

---

## 🎮 PARTIE 2 : RAWG API - Commandes Jeux (GRATUIT)

### Pourquoi RAWG ?
- **Gratuit** : 20,000 requêtes/mois
- **Commandes** : `!gameinfo zelda`, `!suggest`
- **Base de données** : 500,000+ jeux

### Étapes d'installation :

1. **Allez sur** : https://rawg.io/apidocs
2. **Cliquez** "Get API Key" (en haut à droite)
3. **Créez un compte** ou connectez-vous
4. **Allez dans** : Account → Settings → API
5. **Cliquez** "Generate new API key"
6. **COPIEZ** la clé générée

```yaml
# Dans config.yaml
apis:
  rawg_key: "votre_cle_rawg_ici"

rawg:
  api_key: "votre_cle_rawg_ici"  # Même clé
```

**✅ Test :** Après configuration, testez avec `!gameinfo minecraft`

---

## 🤖 PARTIE 3 : OpenAI API - LLM Fallback (OPTIONNEL)

### Quand utiliser OpenAI ?
- **Pas de LLM local** (LM Studio, Ollama)
- **Fallback** si LLM local plante
- **Qualité supérieure** pour réponses complexes

### Coûts OpenAI (2025) :
- **GPT-3.5-turbo** : ~$0.002/1K tokens (très bon rapport)
- **GPT-4** : ~$0.03/1K tokens (premium)
- **Usage bot** : ~$5-15/mois selon activité

### Étapes d'installation :

1. **Allez sur** : https://platform.openai.com/
2. **Créez un compte** ou connectez-vous
3. **Ajoutez** un moyen de paiement (carte requise)
4. **Allez dans** : API Keys (menu gauche)
5. **Cliquez** "Create new secret key"
6. **NOMMEZ** : "KissBot-V1"
7. **COPIEZ** la clé (commence par `sk-`)

```yaml
# Dans config.yaml
apis:
  openai_key: "sk-votre_cle_openai_ici"

llm:
  openai_model: "gpt-3.5-turbo"  # Ou "gpt-4"
  fallback_provider: "openai"
```

**⚠️ Sécurité :** Ne partagez JAMAIS votre clé OpenAI !

---

## 🔄 PARTIE 4 : LLM Local (GRATUIT Alternative)

### Options LLM Local :

**🥇 LM Studio (Recommandé) :**
1. **Téléchargez** : https://lmstudio.ai/
2. **Installez** et lancez
3. **Téléchargez** un modèle (ex: Qwen 7B, LLaMA 8B)
4. **Démarrez** le serveur local (port 1234)

**🥈 Ollama (Linux CLI) :**
1. **Installez** : `curl -fsSL https://ollama.ai/install.sh | sh`
2. **Lancez service** : `sudo systemctl start ollama && sudo systemctl enable ollama`  
3. **Téléchargez modèle** : `ollama pull qwen2.5:7b-instruct`
4. **Endpoint** : `http://127.0.0.1:11434/v1/chat/completions` (port 11434)

📖 **Guide complet** : Voir `OLLAMA_LINUX_SETUP.md` pour installation détaillée, systemd service, monitoring, etc.

```yaml
# Dans config.yaml (LM Studio)
llm:
  enabled: true
  local_llm: true
  provider: "local"
  model_endpoint: "http://127.0.0.1:1234/v1/chat/completions"
  model_name: "qwen2.5-7b-instruct"
```

---

## 📋 PARTIE 5 : Validation Configuration

### Méthode automatique :
```bash
cd KissBot
python3 validate_config.py
```

### Checklist manuelle :

**✅ Twitch (OBLIGATOIRE) :**
- [ ] Token commence par `oauth:`
- [ ] Client ID (app Twitch)
- [ ] Client Secret (app Twitch)  
- [ ] Bot ID (numérique)
- [ ] Channel configuré

**✅ APIs (OPTIONNELLES) :**
- [ ] RAWG key (pour jeux)
- [ ] OpenAI key (pour fallback LLM)

**✅ LLM :**
- [ ] Local : LM Studio running OU
- [ ] Cloud : OpenAI configuré

---

## 🚨 Troubleshooting Fréquent

### "Invalid OAuth token"
- ✅ Token commence par `oauth:`
- ✅ Régénérez sur twitchtokengenerator.com
- ✅ Vérifiez bon compte connecté

### "Failed to join channel"  
- ✅ Nom channel exact (sans #)
- ✅ Channel existe et actif
- ✅ Bot a permissions (si compte séparé)

### "RAWG API Error"
- ✅ Clé copiée entièrement
- ✅ Pas de limite mensuelle dépassée
- ✅ Connexion internet OK

### "OpenAI API Error"
- ✅ Clé commence par `sk-`
- ✅ Crédit disponible sur compte
- ✅ Pas de limite rate dépassée

---

## 🎊 Configuration Exemple Complète

```yaml
# Configuration KissBot V1 complète
bot:
  name: "mon_bot"
  personality: "sympa, cash, passionné de tech"
  debug: true
  cooldown: 5

twitch:
  token: "oauth:abc123def456ghi789"
  client_id: "xyz123uvw456"
  client_secret: "secret789abc123"
  bot_id: "123456789"
  prefix: "!"
  channels: ["mon_channel"]

apis:
  rawg_key: "rawg789def456abc123"
  openai_key: "sk-openai123abc456def789"

llm:
  enabled: true
  local_llm: true
  provider: "local"
  fallback_provider: "openai"
  model_endpoint: "http://127.0.0.1:1234/v1/chat/completions"
  model_name: "qwen2.5-7b-instruct"
  openai_model: "gpt-3.5-turbo"

rawg:
  api_key: "rawg789def456abc123"
```

---

## 🎯 Résumé : Configuration 10 Minutes

1. **[5 min]** Créer app Twitch + générer token
2. **[2 min]** Récupérer RAWG API key (gratuit)
3. **[2 min]** Configurer config.yaml
4. **[1 min]** Valider avec `python3 validate_config.py`

**Total : 10 minutes → KissBot opérationnel !** 🚀

**OpenAI optionnel si vous avez LM Studio local** 💡