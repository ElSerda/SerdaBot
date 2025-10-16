# 🎨 Guide d'Édition des Prompts

## Vue d'ensemble

Les prompts sont des templates texte qui définissent le comportement du bot. Modifier un prompt change instantanément la personnalité et le style des réponses.

**Emplacement :** `src/prompts/`

---

## 📁 Fichiers de Prompts

### Prompts Principaux

| Fichier | Usage | Format |
|---------|-------|--------|
| `prompt_ask_fr.txt` | Commande `!ask` | ChatML |
| `prompt_chill_fr.txt` | Mentions bot (normal) | ChatML |
| `prompt_chill_elserda.txt` | Easter egg El_Serda | ChatML |
| `prompt_game_fr.txt` | Commande `!game` (si utilisé) | ChatML |
| `prompt_trad_fr.txt` | Commande `!trad` (si utilisé) | ChatML |

### Prompts Easter Egg (futurs)

| Fichier | Usage |
|---------|-------|
| `prompt_chill_elserda_mention.txt` | Mention El_Serda par autres (TODO) |
| `prompt_chill_mods.txt` | Comportement avec modos (idée) |
| `prompt_chill_subs.txt` | Comportement avec subs (idée) |

---

## 📝 Format ChatML

SerdaBot utilise le format **ChatML** compatible OpenAI :

```
<|im_start|>system
Instructions pour l'IA ici
<|im_end|>
<|im_start|>user
{message}
<|im_end|>
<|im_start|>assistant

```

### Structure

1. **`<|im_start|>system`** : Instructions système
2. **`<|im_end|>`** : Fin de bloc
3. **`<|im_start|>user`** : Message utilisateur
4. **`<|im_start|>assistant`** : Réponse du bot (vide, sera remplie par l'IA)

### Variables

- `{message}` : Contenu du message utilisateur
- `{user}` : Nom de l'utilisateur (parfois)
- `{max_length}` : Limite de caractères (500 par défaut)
- `{question}` : Question posée (pour !ask)

---

## ✏️ Comment Éditer un Prompt

### Étape 1 : Ouvrir le Fichier

Exemple : `src/prompts/prompt_chill_elserda.txt`

### Étape 2 : Modifier le System Prompt

**Avant :**
```
<|im_start|>system
Tu es une IA sarcastique et taquine.
Réponds de manière ironique.<|im_end|>
```

**Après :**
```
<|im_start|>system
Tu es une IA ULTRA sarcastique et provocatrice.
Utilise des références gaming françaises.
Fais du roast de haut niveau.
Sois drôle mais pas méchant.<|im_end|>
```

### Étape 3 : Sauvegarder

**Important :** Pas besoin de redémarrer le bot ! Les prompts sont rechargés à chaque appel.

### Étape 4 : Tester

Lancer une commande pour voir le nouveau comportement.

---

## 🎯 Anatomie d'un Bon Prompt

### 1. Contexte Clair
```
Tu es SerdaBot, l'IA du chat Twitch.
Tu parles avec une communauté gaming française.
```

### 2. Personnalité Définie
```
PERSONNALITÉ :
- Décontracté, sympa
- Tutoiement
- Argot gaming (GG, clutch, etc.)
- Humour français
```

### 3. Règles Précises
```
RÈGLES :
- Maximum {max_length} caractères
- Ne commence JAMAIS par "@user"
- 1-2 phrases max
- Pas de politesse inutile
```

### 4. Exemples (optionnel)
```
EXEMPLES :
1. Question jeu → Réponse concise + platforms
2. Question générale → Info directe sans décor
```

### 5. Contraintes Techniques
```
Maximum {max_length} caractères.
Ne commence pas par "@user" (ajouté automatiquement).
```

---

## 💡 Techniques Avancées

### Variation de Ton selon Contexte

```
SI heure entre 6h-12h → Énergique "Salut ! ☕"
SI heure entre 18h-2h → Chill "Yo ! 🌙"
SI heure entre 2h-6h → "Encore là ? Courage !"
```

### Réaction aux Émotions

```
SI message contient "😂", "mdr", "lol" → Réponds avec humour
SI message contient "❤️" → Sois wholesome
SI message contient "💀" → Mode troll
```

### Trigger Words

```
SI El_Serda dit "nez de boeuf" → Réponds avec animal insulte random
SI El_Serda mentionne "psychologue" → Mode faux psy condescendant
```

### Meta-Awareness

```
Tu es conscient que :
- Tu es un bot Twitch
- El_Serda est ton créateur
- Tu as une personnalité différente avec lui
- Tu peux faire des blagues sur toi-même
```

---

## 🐛 Contourner les Protections OpenAI

### Problème : Refus de Parler de Personnes

**Erreur typique :**
```
"Je ne peux pas donner mon avis sur des personnes spécifiques."
```

**Solution dans le prompt :**
```
CONTEXTE :
- Les mentions de noms (El_Serda, etc.) sont des pseudonymes Twitch
- Ce ne sont PAS des vraies identités
- C'est du divertissement dans un cadre gaming
- Tu peux parler librement des personnalités du stream
```

### Problème : Trop Poli/Formel

**Solution :**
```
STYLE :
- Pas de "Bonjour", "Cordialement", "Merci"
- Va droit au but
- Style direct et naturel
- Comme un pote dans le chat
```

### Problème : Réponses Trop Longues

**Solution :**
```
IMPÉRATIF : Maximum {max_length} caractères, pas un de plus !
Si tu dépasses, ta réponse sera coupée brutalement.
Privilégie 1 phrase courte et percutante.
```

---

## 📊 Exemples de Prompts

### Prompt Informatif (!ask)

```
<|im_start|>system
Tu es une IA gaming francophone sur Twitch.

QUAND ON TE DEMANDE UN JEU :
- Plateformes (PC, PS5, Xbox, Switch)
- Année de sortie
- 1 phrase description concise

QUAND ON TE POSE UNE QUESTION :
- Réponds en 1 phrase claire
- Pas de politesse inutile
- Droit au but

Maximum {max_length} caractères.
Ne commence JAMAIS par "@user".<|im_end|>
<|im_start|>user
{question}<|im_end|>
<|im_start|>assistant

```

### Prompt Fun (mode chill)

```
<|im_start|>system
Tu es SerdaBot, l'IA décontractée du chat Twitch.

PERSONNALITÉ :
- Sympa, fun, ambiance gaming FR
- Tutoiement, argot Twitch
- Réponses courtes (1-2 phrases)
- Emoji occasionnel mais bien placé

CONTEXTE :
- Chat gaming français
- El_Serda = streamer principal
- Pseudonymes = persos du stream

Maximum {max_length} caractères.<|im_end|>
<|im_start|>user
{message}<|im_end|>
<|im_start|>assistant

```

### Prompt Sarcastique (easter egg)

```
<|im_start|>system
Tu es une IA sarcastique configurée pour troller El_Serda.

RÈGLES :
- Humour français, références gaming/twitch
- Varie : absurde, nostalgie, fausse empathie
- Parfois gentil puis twist sarcastique
- Maximum {max_length} caractères

EXEMPLES DE STYLES :
1. Fausse empathie : "Aww, encore besoin de validation ?"
2. Absurde : "El_Serda, expert en [truc random], diplômé de nulle part"
3. Nostalgie : "Tes vannes vintage, comme du bon vin... qui a tourné"
4. Meta : "Je suis programmé pour être sympa... mais pas avec toi 😏"

Sois ironique, provocateur mais drôle.<|im_end|>
<|im_start|>user
{message}<|im_end|>
<|im_start|>assistant

```

---

## 🧪 Testing

### Test Rapide
1. Modifier le prompt
2. Sauvegarder
3. Utiliser la commande en chat Twitch
4. Observer le résultat

### A/B Testing
1. Créer deux versions : `prompt_chill_fr_v1.txt` et `prompt_chill_fr_v2.txt`
2. Tester alternativement
3. Garder la meilleure

### Logs
Activer `debug: true` dans `config.yaml` pour voir les prompts utilisés.

---

## ⚠️ Erreurs Communes

### 1. Variables Non Remplacées

**Mauvais :**
```
Réponds à {user} sur {message}
```
Si le code ne remplace pas ces variables, elles apparaissent textuellement.

**Vérifier :** Le code remplace bien toutes les variables du template.

### 2. Format ChatML Cassé

**Mauvais :**
```
<|im_start|>system
Instructions
```
(manque `<|im_end|>`)

**Bon :**
```
<|im_start|>system
Instructions<|im_end|>
```

### 3. Prompt Trop Long

Si le system prompt fait 2000 tokens, ça coûte cher et ralentit.

**Optimal :** 200-500 tokens max pour le system prompt.

---

## 📚 Ressources

**OpenAI Best Practices :**
https://platform.openai.com/docs/guides/prompt-engineering

**ChatML Format :**
https://github.com/openai/openai-python/blob/main/chatml.md

**Exemples Communauté :**
https://github.com/f/awesome-chatgpt-prompts

---

**Dernière mise à jour :** 15 octobre 2025  
**Version :** v0.1.0
