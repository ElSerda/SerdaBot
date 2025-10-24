# 🎮 KissBot V1 - Guide Configuration Twitch

## 🎯 Choix Architecture : Bot = Compte Principal ou Secondaire ?

### **Option 1 : Compte Principal comme Bot** ⭐ RECOMMANDÉ
- ✅ **Simple** : Un seul compte à gérer
- ✅ **Rapide** : Pas de création compte supplémentaire
- ✅ **Économique** : Pas de frais additionnels
- ❌ **Limitation** : Le bot parle avec VOTRE nom

### **Option 2 : Compte Séparé pour le Bot** 🤖 PRO
- ✅ **Professionnel** : Bot avec nom distinct (ex: "serda_bot")
- ✅ **Clarté** : Viewers distinguent streamer vs bot
- ✅ **Flexibilité** : Bot peut être modéré séparément
- ❌ **Complexe** : Gestion 2 comptes
- ❌ **Setup** : Plus d'étapes configuration

## 🚀 MÉTHODE 1 : Compte Principal comme Bot (Débutant)

### Étape 1 : Génération Token Principal
1. **Allez sur** : https://twitchtokengenerator.com/
2. **Sélectionnez** : "Bot Chat Token"
3. **Connectez-vous** avec votre compte Twitch principal
4. **Autorisez** les permissions demandées
5. **Copiez** le token généré (commence par `oauth:`)

### Étape 2 : Récupération informations compte
1. **User ID** : Allez sur https://www.streamweasels.com/twitch-tools/username-converter/
   - Entrez votre pseudo Twitch
   - Notez le "User ID" (nombre)

2. **Client ID/Secret** :
   - Allez sur https://dev.twitch.tv/console/apps
   - Cliquez "Register Your Application"
   - **Name** : "MonBot-KissBot" (ou votre choix)
   - **OAuth Redirect URLs** : `http://localhost:3000`
   - **Category** : "Chat Bot"
   - Cliquez "Create"
   - Notez le **Client ID** et générez le **Client Secret**

### Étape 3 : Configuration KissBot
```yaml
# Dans config.yaml
bot:
  name: "votre_pseudo_twitch"  # Votre pseudo principal
  
twitch:
  token: "oauth:votre_token_ici"     # Token du site
  client_id: "votre_client_id"       # De dev.twitch.tv
  client_secret: "votre_secret"      # De dev.twitch.tv
  bot_id: "votre_user_id"           # User ID numérique
  channels: ["votre_pseudo_twitch"]  # Votre channel
```

**✅ Résultat** : Votre compte principal devient le bot !

---

## 🤖 MÉTHODE 2 : Compte Séparé pour Bot (Avancé)

### Étape 1 : Création compte bot
1. **Déconnectez-vous** de Twitch
2. **Créez un nouveau compte** Twitch :
   - Nom : `votre_pseudo_bot` (ex: "serda_bot")
   - Email : Utilisez un email différent ou alias
3. **Vérifiez** le compte par email
4. **Connectez-vous** au nouveau compte bot

### Étape 2 : Configuration compte bot
1. **Avatar/Bio** : Personnalisez le profil bot
2. **Retournez** sur votre compte principal
3. **Allez** dans votre chat Twitch
4. **Tapez** : `/mod votre_pseudo_bot` (donner mod au bot)

### Étape 3 : Génération tokens bot
1. **Connectez-vous** au compte BOT
2. **Allez sur** : https://twitchtokengenerator.com/
3. **Sélectionnez** : "Bot Chat Token"
4. **Autorisez** avec le compte BOT
5. **Copiez** le token bot

### Étape 4 : Informations compte bot
1. **User ID Bot** :
   - https://www.streamweasels.com/twitch-tools/username-converter/
   - Entrez le pseudo du BOT
   - Notez le User ID

2. **Client ID/Secret** (réutilisez celui de la méthode 1 ou créez nouveau)

### Étape 5 : Configuration KissBot
```yaml
# Dans config.yaml
bot:
  name: "votre_pseudo_bot"    # Nom du compte BOT
  
twitch:
  token: "oauth:token_du_bot"      # Token du compte BOT
  client_id: "votre_client_id"     # De dev.twitch.tv  
  client_secret: "votre_secret"    # De dev.twitch.tv
  bot_id: "user_id_du_bot"        # User ID du BOT
  channels: ["votre_pseudo_principal"]  # Votre channel principal
```

**✅ Résultat** : Compte bot séparé rejoint votre channel !

---

## 🔧 Configuration Avancée

### Permissions Twitch Requises
Votre token doit avoir ces scopes :
- `chat:read` - Lire les messages
- `chat:edit` - Envoyer des messages  
- `channel:moderate` - Actions modération (optionnel)
- `whispers:read` - Lire whispers (optionnel)
- `whispers:edit` - Envoyer whispers (optionnel)

### Test de Connexion
```bash
# Lancez KissBot avec debug
./start_kissbot.sh

# Logs attendus :
✅ Bot connecté: votre_bot_name
📺 Channels: [<Channel name: votre_channel>]
🎮 KissBot prêt avec architecture 3-pillar !
```

### Commandes Test dans Chat
```
!ping           # Test basique
@votre_bot hey  # Test mention LLM
!gameinfo zelda # Test API jeux
```

---

## 🚨 Dépannage Courant

### Erreur : "Invalid OAuth token"
- ✅ Vérifiez que le token commence par `oauth:`
- ✅ Régénérez un nouveau token sur twitchtokengenerator.com
- ✅ Vérifiez que vous êtes connecté au bon compte

### Erreur : "Failed to join channel"
- ✅ Vérifiez l'orthographe du nom de channel
- ✅ Le channel doit exister et être actif
- ✅ Si bot séparé : donnez-lui mod avec `/mod bot_name`

### Bot ne répond pas
- ✅ Vérifiez que le bot_id correspond au compte du token
- ✅ Testez avec `!ping` d'abord
- ✅ Vérifiez les logs pour erreurs LLM

### Rate Limit / Spam Protection
- ✅ Attendez 30s entre tests
- ✅ Vérifiez cooldown dans config.yaml
- ✅ Bot nouveau = limitations Twitch temporaires

---

## 📋 Checklist Finale

### Avant Premier Lancement :
- [ ] Token généré et copié dans config.yaml
- [ ] Client ID/Secret configurés
- [ ] Bot_id correspond au compte du token
- [ ] Channel name exact (sans #)
- [ ] Bot a permissions mod si compte séparé
- [ ] LLM local ou OpenAI configuré

### Premier Test :
```bash
./start_kissbot.sh
# Attendez "KissBot prêt"
# Allez dans votre chat Twitch
# Tapez: !ping
# Réponse attendue: "🏓 Pong! ..."
```

**✅ Si !ping fonctionne → KissBot est parfaitement configuré !**

---

## 🎊 Recommandations Finales

### **Débutants** : Utilisez votre compte principal
- Configuration 5 minutes
- Zéro complication
- Parfait pour tester KissBot

### **Streamers Pro** : Créez un compte bot dédié
- Image professionnelle
- Gestion séparée modération  
- Évolutivité future

### **Après Configuration** :
1. **Testez toutes les commandes** (!ping, !gameinfo, @mentions)
2. **Configurez la personnalité** dans config.yaml
3. **Ajustez les cooldowns** selon votre audience
4. **Activez LLM local** ou OpenAI selon préférence

**🎯 KissBot configuré = Stream level UP ! 🚀**