# 🧠 Smart Personality System

## 🎯 Problème Résolu

**Challenge** : Les petits modèles LLM (<7B params) ignorent souvent les instructions de personnalité dans les prompts, rendant le comportement instable et imprévisible.

**Solution** : Système de personnalité intelligent qui s'active automatiquement selon le modèle utilisé.

---

## 💡 Genius Mode : `personality_only_on_cloud`

### Comportement

Quand `personality_only_on_cloud: true` :

1. **Sur LOCAL (petit modèle)** : Personality **désactivée** automatiquement
   - Mode CLEAN factuel même sur `@mention`
   - Réponses stables et prévisibles
   - Logs : `🧠 Personality désactivée sur LOCAL (qwen2.5-1.5b-instruct)`

2. **Sur CLOUD fallback (GPT)** : Personality **réactivée** automatiquement
   - Mode ROAST avec caractère
   - Utilise la puissance de GPT-3.5+ pour personnalité fiable
   - Logs : `🎭 Personality réactivée pour fallback cloud (GPT-3.5)`

### Configuration

```yaml
# config.yaml
llm:
  provider: "local"
  model_name: "qwen2.5-1.5b-instruct"
  
  # 🎭 Flags personality
  use_personality_on_mention: true   # Roast mode sur @mentions
  use_personality_on_ask: false      # Clean mode sur !ask
  personality_only_on_cloud: true    # 💡 GENIUS: Active SEULEMENT sur GPT fallback

bot:
  personality: "sympa, direct, et passionné de tech"
```

---

## 📊 Impact Tests

### GPT-3.5 (AVEC personality)
- **"explique Python"** : 332 → 242 chars (-59% plus direct)
- **"salut !"** : 45 → 77 chars (+19% plus engageant avec emoji)
- **Tone** : Utilise emojis, hashtags, ton conversationnel

### Local 1.5B (SANS personality)
- **"explique Python"** : 250 → 248 chars (<1% différence)
- **"salut !"** : 42 → 44 chars (<5% différence)
- **Tone** : Identique avec ou sans personality

**Conclusion** : Personality n'a quasiment **aucun impact** sur petits modèles (<7B).

---

## 🔄 Workflow Intelligent

### Scénario Normal (Local UP)

```
User: @KissBot salut !
       ↓
1. LLM Local (1.5B) essayé en premier
2. personality_only_on_cloud=true détecté
3. Personality désactivée → Prompt CLEAN
4. Réponse stable : "Salut ! 👋"
```

### Scénario Fallback (Local DOWN)

```
User: @KissBot salut !
       ↓
1. LLM Local échoué (offline/timeout)
2. Fallback vers OpenAI GPT-3.5
3. personality_only_on_cloud=true détecté
4. Personality réactivée → Prompt ROAST
5. Réponse personnalisée : "Yo ! 😎 Envie de discuter tech ? #DevLife"
```

---

## 🎨 Context-Based Modes

### CLEAN Mode (!ask)
```yaml
use_personality_on_ask: false
```
- Factuel, précis, sans fioritures
- Même avec GPT (toujours désactivé sur !ask)
- Idéal pour réponses techniques

### ROAST Mode (@mention)
```yaml
use_personality_on_mention: true
```
- Activé SEULEMENT si `personality_only_on_cloud=false` OU si fallback cloud
- Ton conversationnel, emojis, engagement
- Experience utilisateur améliorée sur GPT

---

## 🚀 Avantages

1. **Fiabilité** : Petits modèles restent stables (pas de personality instable)
2. **Seamless UX** : Fallback transparent vers GPT avec personnalité automatique
3. **Performance** : Local rapide (<1s) + Cloud expressif (quand nécessaire)
4. **Best of Both** : Vitesse locale + caractère cloud sans configuration manuelle

---

## ⚠️ Recommendations

### Pour Small Models (<7B)
```yaml
personality_only_on_cloud: true  # ✅ RECOMMANDÉ
```

### Pour Large Models (7B+)
```yaml
personality_only_on_cloud: false  # Personality fonctionne bien
```

### Pour Cloud Only (GPT/Claude)
```yaml
provider: "openai"
personality_only_on_cloud: false  # Pas de local = pas besoin du flag
use_personality_on_mention: true  # Utiliser personality directement
```

---

## 📝 Logs Exemple

### Local avec personality_only_on_cloud
```
🧠 Personality désactivée sur LOCAL (qwen2.5-1.5b-instruct) - sera activée si fallback cloud
🎯 Prompt CLEAN: "Tu es KissBot, bot Twitch. Réponds EN FRANÇAIS UNIQUEMENT. Max 200 caractères."
```

### Fallback Cloud avec réactivation
```
🔄 Local principal échoué, essai fallback...
🔄 Fallback vers OpenAI...
🎭 Personality réactivée pour fallback cloud (GPT-3.5)
🎯 Prompt ROAST: "Tu es KissBot, sympa, direct, et passionné de tech. Réponds EN FRANÇAIS UNIQUEMENT avec ton CARACTÈRE. Max 200 caractères."
```

---

## 🎯 TL;DR

**Smart Personality** = Meilleur des deux mondes :
- Local fast & stable (sans personality instable)
- Cloud fallback avec caractère (personality auto-activée)
- Zero configuration manuelle
- Experience seamless pour l'utilisateur

**Genius Mode** : Un seul flag qui adapte automatiquement le comportement au modèle LLM utilisé ! 🧠✨
