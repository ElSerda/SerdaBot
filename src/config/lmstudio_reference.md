# 🎛️ LM Studio - Configuration de Référence

Ce fichier documente les **paramètres optimaux** pour LM Studio avec SerdaBot.

---

## 📋 Paramètres recommandés

### **Model Settings** (onglet "Model" dans LM Studio)

```yaml
Temperature:         0.7
Top P:               0.9
Top K:               40-100 (si disponible)
Max Tokens:          60
Presence Penalty:    0.6
Frequency Penalty:   0.4
Stop Sequences:      ["\n", "User:", "Assistant:", "@"]
```

---

## 🎯 Explication des paramètres

### **Temperature (0.7)**
- Contrôle la créativité du modèle
- `0.3` = Très prévisible, répétitif
- `0.7` = **Équilibré** (recommandé pour Twitch)
- `1.0+` = Trop aléatoire, incohérent

### **Top P (0.9)**
- Sélectionne les 90% meilleurs tokens
- Évite les choix trop improbables
- Garde une bonne diversité

### **Top K (40-100)**
- Limite aux K meilleurs tokens
- Complémentaire à Top P
- Réduit encore plus l'aléatoire

### **Max Tokens (60)**
- Limite la longueur des réponses
- **60 tokens ≈ 12-25 mots** (parfait pour Twitch)
- Réduit la latence sur machines lentes

### **Presence Penalty (0.6)**
- Pénalise la **répétition d'idées**
- Évite : "Je suis gentil. Je suis toujours gentil."
- Force le modèle à varier ses concepts

### **Frequency Penalty (0.4)**
- Pénalise la **répétition de mots**
- Évite : "incroyable incroyable incroyable"
- Rend les réponses plus naturelles

### **Stop Sequences**
- `\n` : Coupe à la première ligne (1 phrase max)
- `User:` / `Assistant:` : Évite que le modèle simule un dialogue
- `@` : Évite les mentions intempestives

---

## 🚀 Performance attendue

### **Machine moderne** (GTX 1660+ / RTX)
- Vitesse : **50-100 tok/s**
- Latence : **~1-2 secondes**
- Qualité : Excellente

### **Machine ancienne** (GTX 780 / CPU)
- Vitesse : **3-10 tok/s**
- Latence : **~3-5 secondes**
- Qualité : Très bonne (sous timeout 10s)

---

## 📝 System Prompt utilisé par le bot

```
Bot Twitch FR. Réponds en UNE phrase max (12-25 mots).
Ton fun et complice. Pas d'auto-flatterie. 0-2 émojis max.
Pas de listes, pas de !!!, pas de citations longues.
```

---

## 🔧 Configuration dans LM Studio

1. **Lancer LM Studio**
2. Aller dans **Developer** → **Server**
3. Démarrer le serveur sur `http://localhost:1234/v1`
4. Charger un modèle (ex: Qwen 2.5 1.5B Instruct)
5. Appliquer les paramètres ci-dessus dans l'interface
6. Le bot se connectera automatiquement !

---

## 🎮 Modèles recommandés

### **Petit & Rapide** (1-3B params)
- ✅ **Qwen 2.5 1.5B Instruct** (recommandé)
- ✅ Phi-3 Mini (3.8B)
- Bon pour : Machines lentes, latence minimale

### **Moyen** (7-8B params)
- ✅ Qwen 2.5 7B Instruct
- ✅ Llama 3.2 8B
- Bon pour : RTX 3060+, meilleure qualité

### **Gros** (14B+ params)
- Qwen 2.5 14B Instruct
- Llama 3.1 15B
- Bon pour : RTX 4070+, qualité maximale

---

## 💡 Tips

- **CPU uniquement** : Utilisez un modèle ≤3B (Qwen 2.5 1.5B)
- **GPU <8GB VRAM** : Modèle ≤7B
- **GPU ≥12GB VRAM** : Modèle 14B+ possible
- **Twitch = latence critique** : Privilégiez la vitesse sur la taille

---

## 🆘 Dépannage

### Le bot timeout (>10s)
- ⚠️ Modèle trop gros pour ta machine
- Solution : Passer à un modèle plus petit (1.5B)

### Réponses trop courtes/vides
- ⚠️ `max_tokens` trop bas
- Solution : Augmenter à 100 (mais latence +)

### Réponses génériques ("ma liste de qualités...")
- ✅ Le garde-fou lexical filtre ça automatiquement !
- Le bot réessaiera avec un meilleur prompt

---

📅 **Dernière mise à jour** : Optimisations Twitch (Oct 2025)
