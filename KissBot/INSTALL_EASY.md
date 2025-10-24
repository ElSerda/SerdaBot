# 🚀 KissBot V1 - Installation ONE-LINER

**Le bot Twitch le plus simple à installer au monde !**

## ⚡ Installation ONE-LINER Ultime

### Linux / macOS / WSL
```bash
curl -sSL https://raw.githubusercontent.com/ElSerda/SerdaBot/kissbot/quick-install.sh | bash
```

### Windows PowerShell (Admin)
```powershell
irm https://raw.githubusercontent.com/ElSerda/SerdaBot/kissbot/quick-install.ps1 | iex
```

**C'est TOUT !** Une seule commande → KissBot installé et prêt ! 🎊

## 🎯 Installation Manuelle (si préférée)

### Linux / macOS / WSL
```bash
curl -sSL https://raw.githubusercontent.com/ElSerda/SerdaBot/kissbot/install.sh | bash
```

### Windows PowerShell
1. **Ouvrir PowerShell en Administrateur**
2. **Autoriser les scripts** :
   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
3. **Télécharger et exécuter** :
   ```powershell
   Invoke-WebRequest -Uri "https://raw.githubusercontent.com/ElSerda/SerdaBot/kissbot/install.ps1" -OutFile "install.ps1"
   .\install.ps1
   ```

## ⚙️ Configuration (10 minutes max)

**📚 Guide complet :** [COMPLETE_API_SETUP_GUIDE.md](COMPLETE_API_SETUP_GUIDE.md)

### 🚀 Configuration Express :

1. **Tokens Twitch** (obligatoire - 5 min) :
   - App Twitch : https://dev.twitch.tv/console/apps
   - Bot Token : https://twitchtokengenerator.com/
   - User ID : https://www.streamweasels.com/twitch-tools/username-converter/

2. **RAWG API** (jeux - 2 min) :
   - Clé gratuite : https://rawg.io/apidocs

3. **Configurez `config.yaml`** (2 min)
4. **Validez** : `python3 validate_config.py` (1 min)

### 🎊 Lancement :
```bash
./start_kissbot.sh    # Linux/macOS
.\start_kissbot.ps1   # Windows
```

**✅ Bot LIVE sur Twitch en 10 minutes !**

## 📺 Suivi Installation Temps Réel

L'ultra-installeur affiche **TOUT** en temps réel :
- ✅ Vérification prérequis (Python, Git, connexion)
- 📥 Téléchargement KissBot depuis GitHub  
- 🔧 Création environnement virtuel automatique
- 📦 Installation dépendances Python
- ⚙️ Configuration guidée interactive
- 🚀 Instructions lancement final

**Transparence totale, zero stress !** 🎯

---

## 🏗️ Architecture KISS

- **2,021 lignes** vs 7,468 pour SerdaBot (3x plus léger)
- **Prompts adaptatifs** par modèle LLM
- **Fallback cascade** automatique  
- **Installation 1-clic**
- **Configuration minimal**

## 🤖 Fonctionnalités

- ✅ **Réponses LLM intelligentes** (local + cloud)
- ✅ **Commandes jeux** (!gameinfo, !suggest)
- ✅ **Traduction automatique**
- ✅ **Rate limiting intelligent**
- ✅ **Logs professionnels**
- ✅ **Zero configuration** par défaut

## 📋 Prérequis

- **Python 3.8+**
- **Git**
- **Connexion internet**

L'installeur vérifie et guide pour tout le reste !

---

**Keep It Simple, Stupid! 🎯**