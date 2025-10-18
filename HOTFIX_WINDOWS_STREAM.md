# 🔧 HOTFIX Windows - Phrases coupées (avant stream)

## 🎯 Objectif
Vérifier que les phrases ne sont plus coupées en plein milieu avec `max_tokens_chill=60`

## ✅ Ce qui a été fait sur Linux
- ✅ Tests locaux avec `test_max_tokens_60.py` → OK
- ✅ Config modifié : `max_tokens_chill: 60` (était 45)
- ✅ Commit + push sur GitHub

## 🪟 À FAIRE SUR WINDOWS (machine de production)

### Étape 1 : Mettre à jour le code
```powershell
cd C:\Users\YourUser\SerdaBot
git pull origin main
```

### Étape 2 : Mettre à jour config.yaml
Ouvrir `src\config\config.yaml` et **vérifier** que ces lignes existent :
```yaml
bot:
  max_tokens_ask: 120       # Max tokens pour ASK (détaillé)
  max_tokens_chill: 60      # Max tokens pour CHILL (conversationnel, était 45)
  temperature_ask: 0.4      # Temperature ASK (factuel)
  temperature_chill: 0.7    # Temperature CHILL (créatif)
```

**Si ces lignes sont absentes**, les ajouter après la ligne `model_timeout: 10`

### Étape 3 : Test rapide (optionnel mais recommandé)
**Option A : Test manuel sur Twitch**
1. Lancer le bot : `.\start_bot.ps1`
2. Dans le chat Twitch, taper : `serda_bot que peux tu me dire sur nintendo ?`
3. ✅ Vérifier que la phrase se termine correctement (pas coupée comme "...Super Mario et The Legend of")

**Option B : Test local (si tu veux être sûr)**
```powershell
# Activer venv
.\venv\Scripts\Activate.ps1

# Lancer le test
python scripts\test_max_tokens_60.py
```

### Étape 4 : Redémarrer le bot pour le stream
```powershell
.\start_bot.ps1
```

## 📊 Résultats attendus

### ❌ AVANT (max_tokens=45)
```
"Nintendo est une société japonaise... leurs jeux comme Super Mario et The Legend of"
```
☝️ Phrase coupée net

### ✅ APRÈS (max_tokens=60)
```
"Nintendo est une grande société qui fait des jeux vidéo et des consoles. Ils sont connus pour leurs consoles Nintendo 3DS, Nintendo Switch et leurs jeux comme Super Mario et The Legend of Zelda."
```
☝️ Phrase complète avec point final

## ⚠️ Note importante
- Le fichier `config.yaml` est **local** (pas dans git car contient des tokens)
- Le fichier `config.sample.yaml` est **le template** qui a été mis à jour
- Si tu as besoin de reset ta config, copie `config.sample.yaml` → `config.yaml` et rempli tes tokens

## 🚨 Problème ? 
Si les phrases sont encore coupées :
1. Vérifier que LM Studio utilise bien **Qwen2.5-3B-Instruct**
2. Vérifier dans les logs : `[METRICS] 📤 OUTPUT: X chars, ~Y tokens` (devrait être ~60 tokens max)
3. Augmenter `max_tokens_chill` à 80 si nécessaire (mais teste d'abord 60)

## ⏰ Timeline
- **Maintenant** : Tests locaux Linux ✅
- **Avant le stream (dans ~19h)** : Tests Windows
- **Stream dimanche soir** : Bot live chez l'amie

Bon stream ! 🚀
