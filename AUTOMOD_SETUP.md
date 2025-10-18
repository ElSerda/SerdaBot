# 🔑 Guide : Activer les Scopes AutoMod

## 📋 Ce qui a été ajouté

Le bot peut maintenant gérer l'**AutoMod Twitch natif** via l'API :
- `!addbanword <mot>` → Ajoute à l'AutoMod (bloque AVANT affichage)
- `!removebanword <mot>` → Retire de l'AutoMod
- `!banwords` → Liste les mots bannis
- `!automod <0-4>` → Configure le niveau AutoMod

## ⚠️ MAIS il faut les scopes OAuth

Le token actuel dans `config.yaml` n'a **pas** les permissions pour gérer l'AutoMod.

---

## 🚀 Étapes pour activer (5 minutes)

### Option 1 : Twitch Token Generator (Recommandé)

1. **Va sur** : https://twitchtokengenerator.com/

2. **Choisis** : "Custom Scope Token"

3. **Sélectionne ces scopes** (en PLUS des actuels) :
   ```
   ✅ chat:read
   ✅ chat:edit
   ✅ moderator:manage:blocked_terms  ← NOUVEAU
   ✅ moderator:read:blocked_terms    ← NOUVEAU
   ✅ moderator:manage:automod_settings (optionnel)
   ```

4. **Clique** sur "Generate Token"

5. **Copie le nouveau token** (commence par `oauth:...`)

6. **Remplace dans** `config.yaml` :
   ```yaml
   twitch:
     token: "oauth:NOUVEAU_TOKEN_ICI"
   ```

7. **Redémarre le bot**

---

### Option 2 : Twitch CLI (Pour les pros)

```bash
twitch token -u -s "chat:read chat:edit moderator:manage:blocked_terms moderator:read:blocked_terms"
```

---

## ✅ Vérifier que ça marche

1. **Démarre le bot** : `./start_bot.sh` ou `.\start_bot.ps1`

2. **Regarde les logs** au démarrage :
   ```
   ✅ Pas d'erreur AutoMod → Scopes OK !
   ⚠️ "AutoMod désactivé (config manquante)" → Scopes manquants
   ```

3. **Teste dans le chat** (en tant que MOD) :
   ```
   !addbanword test
   ```

   **Si ça marche** :
   ```
   🚫 Mot 'test' ajouté à l'AutoMod Twitch !
   ```

   **Si ça ne marche pas** :
   ```
   ⚠️ AutoMod API désactivé (config/scopes manquants)
   ```

---

## 🔍 Debug : Vérifier les scopes actuels

### Via Twitch Token Generator
1. Va sur https://twitchtokengenerator.com/
2. Clique sur "Quick Link"
3. Entre ton token (sans `oauth:`)
4. Clique "View Token Details"
5. Regarde la section "Scopes" → doit contenir `moderator:manage:blocked_terms`

---

## 📝 Notes importantes

### Le bot doit être MOD
Même avec les bons scopes, le bot doit être **MOD** sur le canal pour utiliser l'API AutoMod.

```
/mod serda_bot
```

### broadcaster_id requis
L'API AutoMod nécessite le `broadcaster_id` (ID numérique du propriétaire du canal).

**Si absent dans config.yaml**, le bot utilise `bot_id` par défaut (fonctionne si tu stream sur ton propre canal).

**Si tu stream ailleurs**, ajoute dans `config.yaml` :
```yaml
twitch:
  broadcaster_id: "123456789"  # ID du propriétaire du canal
```

**Pour trouver un user ID** : https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/

---

## 🎯 Système sans scopes (fallback)

Si tu n'actives PAS les scopes, le bot fonctionne quand même :
- ✅ `!blocksite` continue de marcher (système local)
- ✅ Toutes les autres commandes fonctionnent
- ❌ `!addbanword`, `!banwords`, `!automod` → Message d'erreur explicite

**Pas de casse**, juste une feature en moins.

---

## 🚨 Problèmes courants

### "AutoMod API désactivé"
→ Token n'a pas les scopes OU config manquante

### "❌ Erreur lors de l'ajout (vérifier scopes OAuth)"
→ Token invalide OU bot pas MOD sur le canal

### "403 Forbidden"
→ Scopes manquants dans le token

---

## ✅ Checklist finale

- [ ] Nouveau token généré avec `moderator:manage:blocked_terms`
- [ ] Token copié dans `config.yaml`
- [ ] Bot redémarré
- [ ] Bot est MOD sur le canal (`/mod serda_bot`)
- [ ] Test avec `!addbanword test`
- [ ] Vérifier dans dashboard Twitch que "test" apparaît

---

**Prêt à tester !** 🚀

Si tu as des problèmes, partage les logs du démarrage du bot.
