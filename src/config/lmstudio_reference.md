# 🎛️ LM Studio - Configuration de Référence

Ce fichier documente les **paramètres optimaux** pour LM Studio avec SerdaBot.

---

## 🎯 TL;DR : Un seul preset suffit !

**LM Studio ne permet qu'un seul profil de paramètres à la fois.**  
→ Configure avec le preset **"Standard Twitch"** ci-dessous.  
→ Les variations de comportement (chill/hype) sont gérées **dans les prompts système**, pas dans LM Studio.

---

## ⚙️ Preset "Standard Twitch" (UNIQUE)

**À configurer dans LM Studio :**

```yaml
Temperature:         0.7
Top-K:               40
Top-P:               0.9
Min-P:               0.05
Repeat Penalty:      1.10
Max Tokens:          50
Limit response:      ON
Stop Sequences:      ["\n", "User:", "Assistant:", "@"]
```

**Ce preset fonctionne pour toutes les commandes** (`!chill`, `!ask`, `!game`) car :
- Les prompts système sont **ultra-stricts** : "UNE phrase (12-25 mots MAX)"
- Le code ajuste les paramètres si besoin (ex: `max_tokens` peut varier par commande)
- Pas besoin de changer la config LM Studio selon la commande

---

## 🎯 Explication des paramètres

### **Temperature (0.7)**
- Contrôle la créativité du modèle
- `0.6` = Plus safe, moins d'impro (Chill/Hello)
- `0.7` = **Équilibré** (recommandé par défaut)
- `0.8` = Plus fun, plus piquant (Hype mode)

### **Top-K (40)**
- Limite aux 40 meilleurs tokens
- Coupe les choix improbables
- Montez à 60 pour mode Hype

### **Top-P (0.9)**
- Sélectionne les 90% meilleurs tokens (cumul de probabilité)
- Complémentaire à Top-K
- `0.85` = Plus strict, `0.92` = Plus varié

### **Min-P (0.05)**
- Coupe les "queues bizarres" de probabilité
- Laisse TOUJOURS activé !
- Évite les tokens vraiment improbables

### **Repeat Penalty (1.10)**
- Pénalise la répétition de tokens
- `1.10` = Équilibré
- `1.15` = Si le bot radote trop
- `1.05` = Mode Hype (peut répéter pour emphase)

### **Max Tokens (50)**
- **50 tokens ≈ 12-25 mots** (parfait pour Twitch one-liner)
- Réduit la latence sur GTX 780
- Plus fiable que "Limit response length" seul

### **Stop Sequences**
- `\n` : Coupe à la première ligne (garantit 1 phrase)
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
Bot Twitch FR, UNE phrase (12-25 mots), ton fun/complice,
pas de /me, 0-2 émojis, pas d'auto-flatterie.
```

**Pourquoi ce format strict ?**
- ✅ Force des réponses courtes (Twitch = latence critique)
- ✅ Évite les pavés et les listes
- ✅ Bloque l'auto-congratulation ("ma liste de qualités incroyables...")
- ✅ Ton léger et fun, pas corporate

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
