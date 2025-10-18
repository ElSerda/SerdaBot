# 🛡️ Guide de Test des Pouvoirs MOD (Sans Danger)

## ⚠️ IMPORTANT : Pourquoi tester ?

Le bot utilise `/timeout {user} 60` pour ban les spam bots.  
**MAIS** : Il a besoin d'être **MOD** sur le canal, sinon ça ne fait rien !

Si le bot n'est pas MOD chez ton amie :
- ❌ Les spammeurs ne seront PAS ban
- ✅ Le bot continuera à fonctionner normalement
- 🚫 Aucun risque de ban accidentel (commande ignorée par Twitch)

---

## 🧪 Test 1 : Vérifier si le bot est MOD (sans risque)

### Sur TON canal (el_serda)

1. **Ouvre ton chat Twitch** : https://www.twitch.tv/el_serda
2. **Vérifie si le bot est MOD** :
   ```
   /mods
   ```
   → Regarde si `serda_bot` est dans la liste

3. **Si le bot n'est PAS MOD**, donne-lui les droits :
   ```
   /mod serda_bot
   ```

4. **Test simple (sans danger)** :
   - Le bot ne timeout QUE si le message correspond aux patterns de spam
   - Teste une commande normale : `!ask test`
   - ✅ Ça doit fonctionner normalement

---

## 🧪 Test 2 : Simulation locale (sans danger)

### Tester AVANT d'aller sur Twitch

```bash
cd /home/Serda/SerdaBot-test/SerdaBot
source venv/bin/activate  # Linux
# OU
.\venv\Scripts\Activate.ps1  # Windows

python scripts/test_mod_safety.py
```

Ce script teste :
- ✅ Quels messages seraient détectés comme spam
- ✅ Quels messages passeraient normalement
- ✅ La détection MOD/Broadcaster
- ⚠️ **AUCUN message n'est envoyé sur Twitch**

---

## 🧪 Test 3 : Sur Twitch (TON canal)

### Option A : Test avec un compte alt (recommandé)

Crée un **compte Twitch de test** et :

1. **Donne MOD au bot** : `/mod serda_bot`
2. **Vérifie** : `/mods` (serda_bot doit apparaître)
3. **Connecte-toi avec le compte test**
4. **Envoie un message avec "streamboo"** :
   ```
   Check out my streamboo link
   ```
5. **Le compte test devrait être timeout 60s**

Si ça marche :
- ✅ Le bot est MOD et fonctionne
- ✅ L'anti-spam est actif

Si ça ne marche pas :
- ❌ Le bot n'est pas MOD (vérifie `/mods`)
- ❌ Vérifie les logs : `🚫 Spam bot détecté: {user}`

---

## 🔍 Patterns de Spam Détectés

Le bot détecte ces patterns (voir `data/blocked_sites.json`) :

```json
[
  "streamboo",
  "viewbot"
]
```

**Exemples qui déclenchent le ban :**
- `"🎁 Check out my streamboo link 🎁"` → Timeout 60s
- `"Get viewbot here!"` → Timeout 60s
- Tout message contenant "streamboo" ou "viewbot"

**Exemples qui NE déclenchent PAS le ban :**
- Messages normaux des viewers
- Commandes du bot (`!ask`, `!game`, etc.)
- Messages des MODs (toujours exemptés)
- Le broadcaster (toujours exempté)

**💡 Pour ajouter des sites bloqués :**
- En live (MOD only) : `!blocksite example.com`
- Voir la liste : `!blockedlist`
- Retirer un site : `!unblocksite example.com`



---

## 🪟 Chez ton amie : Checklist

### AVANT le stream

- [ ] **Demande à ton amie de faire** : `/mod serda_bot`
- [ ] **Vérifie que le bot est MOD** : `/mods`
- [ ] **Test rapide** : Envoie un message normal, vérifie que ça marche

### Si le bot N'est PAS MOD chez ton amie

**Option 1** : Demande-lui de faire `/mod serda_bot`  
**Option 2** : Désactive l'anti-spam temporairement (voir ci-dessous)

---

## 🔧 Désactiver l'anti-spam (si nécessaire)

Si tu veux être 100% sûr de ne pas causer de problèmes :

### Dans `config.yaml` :
```yaml
bot:
  anti_spam: false  # Ajouter cette ligne pour désactiver
```

### Ou dans le code (`src/chat/twitch_bot.py` ligne ~175) :

Commente les lignes du timeout :
```python
# === SPAM BOT DETECTION & BAN (sauf si commande de gestion) ===
if not is_management_command:
    channel_owner = message.channel.name.lower()
    if self.translator.is_spam_bot(user, content, channel_owner):
        print(f"🚫 Spam bot détecté: {user} - Message: {content[:50]}")
        # DÉSACTIVÉ POUR LE STREAM
        # try:
        #     timeout_command = f"/timeout {user} 60"
        #     await message.channel.send(timeout_command)
        #     print(f"✅ Commande timeout envoyée: {user} (60 sec)")
        # except ...
        return
```

---

## 🚨 Que faire si ça part en vrille ?

### Si le bot ban tout le monde (peu probable) :

1. **Arrête le bot** : `Ctrl+C` dans le terminal
2. **Unban manuellement** : `/unban {username}` pour chaque personne
3. **Retire les droits MOD** : `/unmod serda_bot`
4. **Debug le problème** avant de relancer

### Si le bot ne ban RIEN (plus probable) :

- ✅ C'est normal ! Le bot ne ban que les vrais spam bots
- ✅ Les messages normaux des viewers passent toujours

---

## 📊 Résumé : Ce qui peut arriver

| Scénario | Bot est MOD | Bot N'est PAS MOD |
|----------|-------------|-------------------|
| Spam bot arrive | ✅ Timeout 60s | ❌ Rien (mais pas grave) |
| Message normal | ✅ Passe | ✅ Passe |
| Commande `!ask` | ✅ Fonctionne | ✅ Fonctionne |
| Mod envoie message | ✅ Toujours exempt | ✅ Toujours exempt |

**Conclusion** : Même si le bot n'est pas MOD, **il ne cassera rien**. Il ne pourra juste pas ban les spammeurs.

---

## ✅ Recommandations pour le stream

1. **Test sur TON canal** d'abord (avec un compte alt)
2. **Demande à ton amie** de faire `/mod serda_bot` AVANT le stream
3. **Si tu as un doute**, désactive l'anti-spam pour le premier stream
4. **Surveille les logs** pendant les 5 premières minutes

**Le bot est conçu pour être safe** : il ne ban que les patterns de spam évidents, et les MODs sont toujours exemptés.

Bon stream ! 🚀
