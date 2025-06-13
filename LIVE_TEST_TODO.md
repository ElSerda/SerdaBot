# ✅ SerdaBot v0.1.0 – LIVE TEST CHECKLIST

## 🟢 DÉMARRAGE

- [ ] Serveurs lancés avec `bash tools/start_servers.sh`
- [ ] Bot lancé avec `python src/chat/twitch_bot.py`
- [ ] Le message de boot "☕️" apparaît dans le chat

# All passed

## 💬 COMMANDES À TESTER EN LIVE

### 🎯 !ask
- [ ] `!ask Quel est le meilleur Zelda ?`

eky_ia: 🔎 Recherche en cours...

eky_ia: @el_serda The best Zelda game is a matter of personal preference. However, some popular choices among fans include The Legend of Zelda: Ocarina of Time and The Legend of Zelda: Breath of the Wild. These games are known for their engaging storylines, expansive worlds, and innovative gameplay mechanics.Ocarina of Time is often praised for its immersive 3D environments, memorable characters, and groundbreaki

- [ ] Réponse courte avec `@user` et ≤ 500 caractères
- [ ] Console affiche le prompt généré

[ASK] ✅ Réponse envoyée : The best Zelda game is a matter of personal preference. However, some popular choices among fans include The Legend of Zelda: Ocarina of Time and The Legend of Zelda: Breath of the Wild. These games are known for their engaging storylines, expansive worlds, and innovative gameplay mechanics.

Ocarina of Time is often praised for its immersive 3D environments, memorable characters, and groundbreaki
[ASK] Prompt utilisé : User el_serda asks: Quel est le meilleur Zelda ?
[18:01:40] ✅ Prêt à écouter de nouvelles commandes.

# Ne cut pas a dernier point vue, avant de tronquer sous les 500 caracteres.

### 🎮 !game
- [ ] `!game Celeste`
- [ ] Résumé correct (source IGDB ou Steam)
- [ ] Affiche bien : nom, plateforme(s), année, lien IGDB
- [ ] Résumé bien tronqué si trop long
- [ ] Console affiche : source résumé, langues détectées

eky_ia: 🎮 Recherche du jeu...

eky_ia: @el_serda 🎮 Celeste (?, Google Stadia, PS4, Linux, PC, Mac, Xbox, Switch) : Help Madeline survive her inner demons on her journey to the top of Mountain, in this super-tight platformer from the creators of TowerFall. Brave hundreds of hand-crafted challenges, uncover devious secrets, and piece together the mystery of the mountain. (voir + : https://www.igdb.com/games/celeste) (cooldown: 10s)

# Platform "?" et Google Stadia a changer pour Stadia.

### 🌍 !trad
- [ ] `!trad Hello, is this working?`
- [ ] Traduction correcte (en → fr)
- [ ] Console affiche : langue détectée, texte traduit
- [ ] Réponse formatée : `📥 (en → fr) : ...`

# Commande a crée !

### 🧘 Chill (mention sans !ask)
- [ ] `eky_ia comment tu vas ?`
- [ ] Réponse chill ou contextuelle (pas de mention `@user`)
- [ ] Prompt affiché dans console
- [ ] Réponse ≤ 500 caractères

El_Serda: eky_ia comment tu vas ?

eky_ia: I’m going to a wedding!It’s been a while since I’ve been to one, and I’m really looking forward to it. It’s also my first time attending a French wedding so it should be an interesting experience. We are still in the process of getting all our ducks in a row with passports and invitations, but it will happen soon enough!As you may remember from my post last year about weddings around the world

[CHILL] Prompt: comment tu vas ?
[CHILL] Final: I’m going to a wedding!

It’s been a while since I’ve been to one, and I’m really looking forward to it. It’s also my first time attending a French wedding so it should be an interesting experience. We are still in the process of getting all our ducks in a row with passports and invitations, but it will happen soon enough!

As you may remember from my post last year about weddings around the world
[18:05:01] ✅ Prêt à écouter de nouvelles commandes.

## 🧪 DÉBOGAGE

- [ ] Aucun message d’erreur `httpx`, `500`, `timeout`
# No error
- [ ] Les réponses ne dépassent pas la limite Twitch
# Sa depend
- [ ] Le bot ignore bien ses propres messages (`message.echo`)
# On dirait que c'est bon
- [ ] Aucune boucle infinie ou crash après plusieurs requêtes

## 🔒 CONFIDENTIALITÉ

- [ ] `config.yaml` n'est **pas** versionné
- [ ] Seul `config.sample.yaml` est présent sur GitHub
