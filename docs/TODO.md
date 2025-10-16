# 📋 SerdaBot TODO List

## 🔥 En Production (Stable)

✅ Easter egg El_Serda fonctionnel (mode sarcastique)  
✅ Commandes avec aliases multiples (`!game`, `!jeu`, `!gameinfo`, etc.)  
✅ OpenAI GPT-3.5-turbo intégration  
✅ Bot Twitch stable avec cooldown optimisé  
✅ Commande !game avec plateformes + infos IGDB/Steam  
✅ Commande !ask pour questions  
✅ **Système de traduction automatique complet** 🌐

---

## 🆕 NOUVEAU : Système de Traduction (Octobre 2025)

✅ **Auto-traduction pour devs anglophones**  
✅ **Whitelist avec `!adddev @user`**  
✅ **Traduction manuelle `!translate <texte>`**  
✅ **Protection anti-spam bots**  
✅ **Cache performant**  
✅ **Documentation complète** (docs/TRANSLATION.md)

**Commandes :**
- `!adddev @user` - Ajouter dev à whitelist (mod only)
- `!removedev @user` - Retirer dev de whitelist (mod only)
- `!listdevs` - Liste des devs whitelistés (mod only)
- `!translate <texte>` - Traduire FR↔EN (mod only)

**Fichiers créés :**
- `src/utils/smart_translator.py` - Moteur de traduction
- `src/core/commands/translation_commands.py` - Commandes
- `docs/TRANSLATION.md` - Documentation
- `tools/test_translation.py` - Tests
- `tools/install_translation.sh` - Installation

**Installation :**
```bash
bash tools/install_translation.sh
```

---

## 🚧 TODO Priorité Haute

### 1. Fix Prompt Chill (mentions El_Serda)
**Problème :** Quand un user mentionne @El_Serda, OpenAI refuse de répondre ("Je ne peux pas donner mon avis sur des personnes")

**Solution :**
- Corriger `chill_command.py` pour utiliser correctement `{message}` dans le template
- Le prompt `prompt_chill_fr.txt` est déjà à jour avec les bonnes instructions
- Code à modifier : 
  ```python
  # Remplacer:
  prompt = prompt_template.replace("{user}", user).replace("{max_length}", "500")
  prompt += f"\n\nMessage de {user}: {content}"
  
  # Par:
  prompt = prompt_template.replace("{message}", content).replace("{max_length}", "500")
  ```

**Impact :** Le bot pourra répondre aux questions "Que penses-tu de El_Serda ?" de manière taquine

---

### 2. Tester les Alias de Commandes
**Nouveaux alias implémentés mais non testés :**
- `!jeu <nom>` (FR unique)
- `!gameinfo <nom>` (explicite)
- `!sb game <nom>` (branding SerdaBot)
- `!question <texte>` (alias !ask)
- `!translate <texte>` (alias !trad)

**Test à faire :** Vérifier que tous les alias fonctionnent en prod

---

### 3. Créer Prompt Sarcastique Léger (Mentions)
**Fichier :** `src/prompts/prompt_chill_elserda_mention.txt` (déjà créé)

**But :** Quand quelqu'un MENTIONNE El_Serda dans un message, le bot utilise ce prompt "sarcastique léger" au lieu du prompt normal.

**Différence comportements :**
- Autre user mentionne El_Serda → Sarcastique léger
- El_Serda parle lui-même → Destruction totale (prompt actuel)

**Code à ajouter dans `chill_command.py` :**
```python
# Détecter mention d'El_Serda dans le contenu
if "el_serda" in content.lower() or "@el_serda" in content.lower():
    # Charger prompt sarcastique léger
    easter_path = os.path.join(prompt_dir, 'prompt_chill_elserda_mention.txt')
```

---

## 🎯 TODO Priorité Moyenne

### 4. Optimiser Coûts OpenAI
**Options :**
- [ ] Monitorer usage API (combien $/mois actuellement ?)
- [ ] Tester `gpt-4o-mini` (meilleure qualité, +50% prix)
- [ ] Ou revenir à `gpt-3.5-turbo` si budget serré

**Calcul rentabilité :**
- Si > 20€/mois → Considérer modèle local sur VPS/GPU dédié
- Si < 10€/mois → Rester sur OpenAI

---

### 5. Documentation à Jour
**Fichiers outdated :**
- `README.md` mentionne Mistral local (faux, c'est OpenAI maintenant)
- `PROJECT_STRUCTURE.md` ne mentionne pas l'easter egg
- Pas de doc sur les alias

**À créer :**
- [ ] `docs/EASTER_EGG.md` - Explication du système easter egg
- [ ] `docs/COMMANDS.md` - Liste complète des commandes + alias
- [ ] `docs/PROMPTS.md` - Guide d'édition des prompts
- [ ] Mettre à jour README avec config OpenAI

---

### 6. Améliorer Easter Egg
**Idées :**
- [ ] Varier les styles de roast (absurde, nostalgique, fausse empathie, etc.)
- [ ] Ajouter des "trigger words" spécifiques (nez de boeuf → animal insulte)
- [ ] Contexte temporel (heure de la journée = ton différent)
- [ ] Easter eggs pour d'autres users (modos, subs, etc.)

**Fichier à éditer :** `src/prompts/prompt_chill_elserda.txt`

---

## 💡 TODO Future (Nice to Have)

### 7. Setup VPS + Modèle Local
**Matériel prévu :**
- PC Streaming : RTX 5080 + Ryzen 9950X3D
- PC IA/Bots : RTX 3080 + i7-10700K

**Plan :**
1. Installer modèle local (Mistral-7B-Instruct Q5_K_M)
2. Setup llama.cpp ou Ollama
3. Modifier `config.yaml` pour utiliser endpoint local
4. Comparer qualité OpenAI vs local
5. Si OK → Migrer complètement (coût 0€/mois)

**ROI :** ~6 mois si usage intensif du bot

---

### 8. Statistiques & Analytics
- [ ] Tracker commandes les plus utilisées
- [ ] Logger interactions par user
- [ ] Dashboard usage bot (Grafana ?)
- [ ] Alertes si coût OpenAI > seuil

---

### 9. Commandes Additionnelles
**Idées communauté :**
- `!clip` - Créer un clip du moment
- `!poll` - Lancer un sondage
- `!quote` - Citations du stream
- `!uptime` - Temps de stream
- `!lurk` - Mode lurk sympathique

**Note :** Vérifier compatibilité avec Nightbot/StreamElements avant

---

### 10. Mode Développement Améliore
- [ ] Hot-reload des prompts (pas besoin de restart bot)
- [ ] Commande `!sb reload` pour recharger config (modos only)
- [ ] Mode debug activable/désactivable en live
- [ ] Logs structurés (JSON) pour parsing

---

## 🐛 Bugs Connus

### Bot non vérifié - Rate Limit Twitch
**Symptôme :** Certains messages ne s'affichent pas en chat

**Solutions :**
1. ✅ Cooldown augmenté à 10s (fait)
2. ✅ Message "Recherche en cours" supprimé (fait)
3. ⏳ Donner mod au bot : `/mod serda_bot` (à faire)
4. ⏳ Demander vérification bot sur dev.twitch.tv (long terme)

---

## 📝 Notes

**Dernière mise à jour :** 15 octobre 2025  
**Version bot :** v0.1.0 (en prod)  
**Model actuel :** OpenAI GPT-3.5-turbo  
**Statut :** Stable, succès en production ✅

**Contact :** El_Serda  
**Repo :** SerdaBot-test/SerdaBot
