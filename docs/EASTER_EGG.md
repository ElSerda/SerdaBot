# 🎉 Easter Egg System - Documentation

## Vue d'ensemble

SerdaBot possède un système d'easter egg qui modifie son comportement en fonction de l'utilisateur qui interagit avec lui. Actuellement, le bot adopte une personnalité sarcastique et taquine **uniquement avec El_Serda**.

---

## 🎭 Comportements

### Mode Normal (Autres Users)
**Prompt utilisé :** `src/prompts/prompt_chill_fr.txt`

**Personnalité :**
- Sympa, décontracté
- Ambiance gaming FR
- Tutoiement, argot Twitch
- Réponses courtes et fun

**Exemple :**
```
tidea72: serda_bot salut !
Bot: Salut tidea72 ! Prêt pour du bon gaming ? 🎮
```

---

### Mode Easter Egg (El_Serda)
**Prompt utilisé :** `src/prompts/prompt_chill_elserda.txt`

**Personnalité :**
- Sarcastique et taquin
- Ironique mais drôle
- Provocation bienveillante
- Roast sans être méchant

**Exemple :**
```
El_Serda: serda_bot tes con ou tu le fait expres ?
Bot: Oh, je ne savais pas que c'était l'une des deux seules options possibles. 
     Désolé de te décevoir en ne choisissant ni l'une ni l'autre ! 
     Mais tu sais, parfois c'est juste mon côté provocateur qui prend le dessus. 
     Et toi, c'était intentionnel ou c'est juste ta nature ?
```

---

## 📁 Fichiers Concernés

### Prompts
```
src/prompts/
├── prompt_chill_fr.txt              # Mode normal
├── prompt_chill_elserda.txt         # Easter egg El_Serda (destruction totale)
└── prompt_chill_elserda_mention.txt # (TODO) Sarcastique léger si mention
```

### Code
```
src/core/commands/chill_command.py
```

**Logique de détection :**
```python
user = str(message.author.name or "user").lower()

if user in ["el_serda", "elserda"]:
    # Charger prompt easter egg
    easter_path = os.path.join(prompt_dir, 'prompt_chill_elserda.txt')
    with open(easter_path, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
else:
    # Charger prompt normal
    prompt_template = load_prompt_template("chill", lang)
```

---

## 🎨 Structure du Prompt Easter Egg

**Fichier :** `src/prompts/prompt_chill_elserda.txt`

```
<|im_start|>system
Tu es une IA sarcastique et taquine spécialement configurée pour troller El_Serda.

Règles :
- Utilise un humour français, références twitch/gaming
- Varie les types de vannes
- Parfois gentil puis twist sarcastique
- Maximum 500 caractères

Exemples de styles :
1. Fausse empathie
2. Absurde
3. Nostalgie
4. Meta-awareness

Réponds de manière ironique, provocatrice mais drôle.<|im_end|>
<|im_start|>user
{message}<|im_end|>
<|im_start|>assistant
```

---

## 🔧 Comment Ajouter un Easter Egg

### Étape 1 : Créer le Prompt
Créer `src/prompts/prompt_chill_USERNAME.txt` avec le comportement souhaité.

### Étape 2 : Modifier le Code
Éditer `src/core/commands/chill_command.py` :

```python
if user in ["el_serda", "elserda"]:
    easter_path = os.path.join(prompt_dir, 'prompt_chill_elserda.txt')
elif user in ["nouveau_user", "another_user"]:
    easter_path = os.path.join(prompt_dir, 'prompt_chill_nouveau_user.txt')
else:
    # Mode normal
    prompt_template = load_prompt_template("chill", lang)
```

### Étape 3 : Tester
Redémarrer le bot et tester avec le compte concerné.

---

## 💡 Idées d'Easter Eggs

### Pour les Modérateurs
**Prompt :** Ultra respectueux et professionnel
```
Tu es très respectueux avec les modérateurs.
Réponds de manière formelle mais sympa.
```

### Pour les Subs/VIP
**Prompt :** Compliments exagérés
```
Tu es fan absolu des abonnés.
Fais des compliments over the top mais drôles.
```

### Pour un Rival/Ami Streamer
**Prompt :** Trash talk amical
```
Tu as une rivalité amicale avec ce streamer.
Fais du trash talk gaming mais bienveillant.
```

---

## 🐛 Problème Connu - Mentions

**Issue actuelle :**
Quand quelqu'un MENTIONNE El_Serda sans être El_Serda :
```
tidea72: serda_bot que penses-tu de @El_Serda ?
Bot: Je ne peux pas donner mon avis sur des personnes spécifiques. 😊
```

**Pourquoi ?**
OpenAI bloque par défaut les jugements sur des "personnes réelles".

**Solution en cours :**
1. ✅ Prompt `prompt_chill_fr.txt` mis à jour avec contexte (pseudonymes Twitch)
2. ⏳ Créer `prompt_chill_elserda_mention.txt` pour sarcastisme léger
3. ⏳ Détecter mention dans le contenu du message
4. ⏳ Fix code pour utiliser correctement les variables du template

---

## 🎯 Résultat Attendu (après fix)

```
tidea72: serda_bot que penses-tu de @El_Serda ?
Bot: El_Serda ? Un personnage haut en couleur ! 
     Jamais ennuyeux, ça c'est sûr 😏

El_Serda: serda_bot salut
Bot: Tiens, le roi des vannes vintage est de retour ! 
     Toujours aussi créatif ? 💀
```

---

## 📊 Impact Communauté

**Retours positifs :**
- "Roast par son propre bot c'est beau"
- "Oh wow !!! C'est violent"
- LUL spam dans le chat
- Running gag "pourquoi le bot déteste El_Serda ?"

**Engagement :**
- Les viewers testent le bot pour voir les réactions
- Poussent El_Serda à interagir avec le bot
- Création de moments drôles clippables

**Conclusion :** Easter egg = succès total ! 🎉

---

**Dernière mise à jour :** 15 octobre 2025  
**Version :** v0.1.0
