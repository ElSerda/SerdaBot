# 🚀 Guide Rapide - SerdaBot Production

Guide rapide pour démarrer et maintenir SerdaBot en production avec Qwen 2.5-1.5B.

---

## ⚡ Démarrage Rapide

### 1. Prérequis

- **Python 3.10+**
- **LM Studio** installé et lancé
- **Qwen2.5-1.5B-Instruct-Q4_K_M.gguf** chargé dans LM Studio
- Tokens Twitch configurés dans `src/config/config.yaml`

### 2. Installation

```bash
# Clone le repo
git clone https://github.com/ElSerda/SerdaBot.git
cd SerdaBot

# Installe les dépendances
pip install -r requirements.txt

# Configure les secrets (copie template)
cp src/config/config.yaml.example src/config/config.yaml
nano src/config/config.yaml  # Ajoute tes tokens Twitch/OpenAI
```

### 3. Vérification LM Studio

```bash
# Vérifie que LM Studio tourne
curl http://127.0.0.1:1234/v1/models

# Test rapide modèle
python scripts/smoke_model.py
```

### 4. Lancement

```bash
# Linux/macOS
bash start_bot.sh

# Windows
.\start_bot.ps1
```

---

## 🤖 Modèle Production

**Qwen 2.5-1.5B-Instruct-Q4_K_M** (optimal ratio perf/ressources)

### Config LM Studio
- **Endpoint**: `http://127.0.0.1:1234/v1/chat/completions`
- **Laisse LM Studio gérer**: GPU layers, context size, etc.
- **Pas besoin ajuster**: Le bot envoie températures/tokens optimaux

### Performances Validées
- ✅ 93% succès ASK (≤250 chars)
- ✅ 80% succès CHILL (1-5 mots)
- ✅ 0.1-0.4s latence (acceptable live)
- ✅ 0 hallucinations (85 cas testés)

📖 **Détails**: Voir `docs/MODEL_CONFIG.md`

---

## 🎮 Commandes Twitch

| Commande | Usage | Exemple |
|----------|-------|---------|
| `!ask <question>` | Question factuelle | `!ask c'est quoi python ?` |
| `@serda_bot <message>` | Interaction fun/cool | `@serda_bot salut !` → "Yo." |
| `!game <titre>` | Info jeu vidéo | `!game Elden Ring` |
| `!trad <texte>` | Traduction FR | `!trad hello world` |

### Mode ASK
- **But**: Réponses concises et claires
- **Limite**: 200 chars prompt → réel ≤250 chars
- **Exemples**:
  - "python" → "Langage populaire pour scripts et IA."
  - "blockchain" → "Technologie de registre décentralisé sécurisé."

### Mode CHILL
- **But**: Réponses ultra-courtes fun/cool
- **Limite**: 1-5 mots maximum
- **Exemples**:
  - "lol" → "Marrant."
  - "t'es qui toi ?" → "Le bot du stream."
  - "bravo" → "Incroyable."

---

## 🔧 Configuration

### Fichiers Clés

```
src/
  config/
    config.yaml          # SECRETS (tokens Twitch/OpenAI) - IGNORÉ GIT ⚠️
  prompts/
    prompt_loader.py     # Prompts ASK/CHILL optimaux + few-shot
  utils/
    model_utils.py       # API calls LM Studio (config dynamique)
  chat/
    twitch_bot.py        # Bot Twitch principal
```

### Variables Importantes

**config.yaml** (secrets):
```yaml
bot:
  channel: ton_channel_twitch
  model_endpoint: http://127.0.0.1:1234/v1/chat/completions
  openai_model: "gpt-4o-mini"  # Fallback si LM Studio down (100% succès, 4x moins cher)
  cooldown: 10  # Secondes entre réponses

twitch:
  token: oauth:xxxxx
  client_id: xxxxx
  client_secret: xxxxx

openai:
  api_key: sk-proj-xxxxx  # Fallback GPT-4o-mini si LM Studio down
```

**prompt_loader.py** (prompts):
```python
SYSTEM_ASK_FINAL = """Maximum 200 caractères par réponse."""
SYSTEM_CHILL_FINAL = """1-5 mots maximum. Style décontracté."""
```

**model_utils.py** (config API):
```python
# ASK: déterministe, explications complètes
temperature = 0.4
max_tokens = 80
stop = ["\n\n"]

# CHILL: stable, ultra court
temperature = 0.5
max_tokens = 20
stop = None
```

---

## 🧪 Tests

### Test Rapide (15 cas)
```bash
python personnal/tests/test_ask_200_chars.py
```

### Test Massif (85 cas)
```bash
python personnal/tests/test_production_final.py
```

### Test Live (smoke test)
```bash
# Vérifie endpoint LM Studio
python scripts/smoke_model.py

# Vérifie bot complet (sans Twitch)
python scripts/smoke_bot.py
```

---

## 🐛 Troubleshooting

### Bot ne répond pas

1. **Vérifie LM Studio**:
   ```bash
   curl http://127.0.0.1:1234/v1/models
   ```
   Si erreur: Relance LM Studio et charge Qwen2.5-1.5B-Instruct-Q4_K_M

2. **Vérifie logs**:
   ```bash
   tail -f logs/serdabot.log
   ```

3. **Vérifie cooldown** (10s entre messages):
   - User doit attendre 10s entre commandes

### Réponses trop longues

1. **Vérifie prompts** (`src/prompts/prompt_loader.py`):
   ```python
   SYSTEM_ASK_FINAL  # Doit contenir "200 caractères"
   SYSTEM_CHILL_FINAL  # Doit contenir "1-5 mots"
   ```

2. **Vérifie config** (`src/utils/model_utils.py`):
   ```python
   optimal_max_tokens = 80 if mode == "ask" else 20
   ```

3. **Re-run tests validation**:
   ```bash
   python personnal/tests/test_ask_200_chars.py
   ```

### Réponses chinoises

❌ **Résolu en production** (prompts français natifs + few-shot)

Si ça arrive:
1. Vérifie `SYSTEM_ASK_FINAL` et `SYSTEM_CHILL_FINAL` en français
2. Vérifie few-shot enrichi activé (mode chill)

### LM Studio down → Fallback OpenAI

Le bot bascule automatiquement sur **GPT-4o-mini** si LM Studio indisponible.

**Logs attendus**:
```
[MODEL] ⚠️ LM Studio indisponible
[MODEL] 🌐 Fallback OpenAI (GPT-4o-mini)...
```

**Performances fallback**:
- ASK: 100% ≤250 chars (188 chars moyenne, 1.52s)
- CHILL: 100% ≤5 mots (3.8 mots moyenne, 0.67s)
- Coût: 4x moins cher que GPT-3.5-turbo

---

## 📊 Monitoring

### Métriques Logs

Le bot log automatiquement:
```
[METRICS] 📥 INPUT: 45 chars, ~11 tokens
[METRICS] 📤 OUTPUT: 28 chars, ~7 tokens
[METRICS] ⚡ Durée: 0.23s, 30.4 tok/s
```

### Performances Attendues

**ASK**:
- 93% réponses ≤250 chars
- Moyenne: 136 chars
- Latence: ~0.4s

**CHILL**:
- 80% réponses ≤5 mots
- Moyenne: 2.6 mots
- Latence: ~0.1s

**Alertes**:
- ⚠️ Si latence >1s: Machine surchargée ou LM Studio lent
- ⚠️ Si >500 chars: Prompt modifié par erreur

---

## 🔄 Maintenance

### Mise à jour modèle

Si upgrade hardware → Qwen 2.5-7B (100% succès validé):
1. Télécharge `Qwen2.5-7B-Instruct-Q4_K_M.gguf`
2. Charge dans LM Studio
3. Relance bot (config identique, performances meilleures)

### Backup config

**IMPORTANT**: `config.yaml` contient secrets, **pas committé** Git ✅

Backup manuel:
```bash
cp src/config/config.yaml src/config/config.yaml.backup
```

### Rollback version

Si problème après update:
```bash
git checkout v0.1.0-alpha  # Dernière version stable
pip install -r requirements.txt
```

---

## 📚 Documentation Complète

- **Model Config**: `docs/MODEL_CONFIG.md` (détails techniques optimisation)
- **Tests Archive**: `personnal/tests/README.md` (historique 17 tests)
- **Changelog**: `CHANGELOG.md` (historique versions)
- **Commands**: `COMMANDS.md` (liste commandes complètes)
- **Structure**: `PROJECT_STRUCTURE.md` (architecture code)

---

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/ElSerda/SerdaBot/issues)
- **Twitch**: [@El_Serda](https://twitch.tv/el_serda)
- **Docs**: `/docs` dans ce repo

---

## 🎯 Checklist Démarrage

- [ ] LM Studio installé et lancé
- [ ] Qwen2.5-1.5B-Instruct-Q4_K_M.gguf chargé
- [ ] `config.yaml` configuré (tokens Twitch)
- [ ] `pip install -r requirements.txt` OK
- [ ] `python scripts/smoke_model.py` OK
- [ ] `bash start_bot.sh` OK
- [ ] Bot répond sur Twitch ✅

**Si tout ✅ → Prêt pour production ! 🎉**
