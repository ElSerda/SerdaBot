# Système de Traduction Automatique
## Smart Translation System

---

## 🎯 **CONCEPT**

Système hybride de traduction pour faciliter la communication entre devs anglophones et communauté francophone :

- **Whitelist-based auto-translation** : Traduction automatique pour les devs enregistrés
- **Manual translation** : Commande `!translate` pour traductions ponctuelles
- **Bot spam protection** : Filtre les bots de viewbot automatiquement

---

## 🛠️ **COMMANDES**

### **Pour les Modérateurs**

#### `!adddev @username`
Ajoute un utilisateur à la whitelist pour auto-traduction.

**Exemple :**
```
!adddev @DevJohn
```
**Résultat :** Tous les messages anglais de @DevJohn seront automatiquement traduits en français.

---

#### `!removedev @username`
Retire un utilisateur de la whitelist.

**Exemple :**
```
!removedev @DevJohn
```

---

#### `!listdevs`
Affiche la liste des devs whitelistés.

**Exemple :**
```
!listdevs
```
**Résultat :** `📋 Devs whitelistés (2): @DevJohn, @DevMaria`

---

#### `!translate <texte>` (ou `!trad <texte>`)
Traduit manuellement un message FR↔EN.

**Exemples :**
```
!translate How do I test this feature?
```
**Résultat :**
```
🇬🇧 How do I test this feature?
🇫🇷 Comment tester cette fonctionnalité ?
```

```
!translate Tu peux lancer le script start.sh
```
**Résultat :**
```
🇫🇷 Tu peux lancer le script start.sh
🇬🇧 You can run the start.sh script
```

---

## 🤖 **AUTO-TRADUCTION**

### **Comment ça marche ?**

1. **Dev ajouté à la whitelist** avec `!adddev @DevName`
2. **Dev écrit en anglais** dans le chat
3. **Bot détecte automatiquement** la langue (>= 3 mots)
4. **Bot traduit et envoie** dans le chat

**Exemple :**

```
DevJohn: Hey, how can I test the new API endpoint?
```

**Bot répond automatiquement :**
```
serda_bot: 🌐 @DevJohn: Hey, how can I test the new API endpoint?
           └─ 🇫🇷 Salut, comment puis-je tester le nouveau endpoint de l'API ?
```

---

## 🔒 **PROTECTION ANTI-SPAM**

Le système **ignore automatiquement** :
- ✅ Les bots connus (Nightbot, StreamElements, etc.)
- ✅ Les viewbots (détection par pattern)
- ✅ Les commandes (`!help`, `!game`, etc.)
- ✅ Les messages trop courts (< 3 mots)

---

## ⚙️ **CONFIGURATION**

### Dans `config.yaml` :

```yaml
bot:
  auto_translate: true  # Active/désactive l'auto-traduction
```

### Whitelist :

La liste des devs est stockée dans `data/dev_whitelist.json` :

```json
[
  "devjohn",
  "devmaria"
]
```

---

## 📊 **PERFORMANCES**

- **Temps de traduction** : ~200ms par message
- **Cache** : Les traductions répétées sont mises en cache
- **Gratuit** : Utilise l'API publique de Google Translate (pas de clé requise)
- **Limite** : ~500k caractères/jour (largement suffisant pour un chat Twitch)

---

## 🎯 **USE CASES**

### **Scénario 1 : Dev rejoint pour tester**

1. Mod : `!adddev @NewDev`
2. NewDev écrit en anglais → Auto-traduit
3. Fin de session : `!removedev @NewDev`

---

### **Scénario 2 : Question ponctuelle**

Dev : "What's the server URL?"  
Mod : `!translate What's the server URL?`  
Bot traduit → Communauté comprend → Streamer répond

---

### **Scénario 3 : Réponse du streamer**

Streamer : `!translate L'URL du serveur est http://localhost:8000`  
Bot traduit → Dev comprend → Problème résolu

---

## 🚀 **INSTALLATION**

```bash
# 1. Installer la dépendance
pip install deep-translator==1.11.4

# 2. Le répertoire data/ sera créé automatiquement
# 3. Redémarrer le bot
bash tools/start_servers.sh
```

---

## 🐛 **DÉPANNAGE**

### **La traduction ne fonctionne pas**

1. Vérifier que le dev est whitelisté : `!listdevs`
2. Vérifier que `auto_translate: true` dans `config.yaml`
3. Vérifier que le message a >= 3 mots
4. Vérifier que le message est en anglais

### **Faux positifs (traduction incorrecte)**

- Le système détecte la langue avec ~90% de précision
- Pour les messages ambigus, utiliser `!translate` manuellement

---

## 📝 **NOTES**

- **Commandes réservées aux mods** : Évite le spam de commandes
- **Pas de cooldown** : Auto-traduction ne compte pas dans le cooldown du bot
- **Cache intelligent** : Messages répétés traduits instantanément

---

## ✅ **AVANTAGES**

- ✅ **Léger** : Pas de model local, utilise une API externe
- ✅ **Gratuit** : Pas de clé API requise
- ✅ **Rapide** : ~200ms par traduction
- ✅ **Précis** : Qualité Google Translate
- ✅ **Flexible** : Auto + manuel selon les besoins
- ✅ **Anti-spam** : Filtre les bots automatiquement
