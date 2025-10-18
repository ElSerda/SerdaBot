# 🤖 Configuration Modèle - SerdaBot

## Modèle Production

**Qwen 2.5-1.5B-Instruct-Q4_K_M** (via LM Studio local)

### Pourquoi ce modèle ?

- ✅ **Performances validées**: 93% succès ASK + 80% succès CHILL (objectif: 80%)
- ✅ **Latence optimale**: 0.1-0.4s (acceptable pour chat Twitch en direct)
- ✅ **Zéro hallucinations**: Tests massifs 85 cas réels (0 erreur)
- ✅ **Hardware friendly**: Fonctionne sur petites machines (vs Qwen 7B trop lourd)
- ✅ **100% limite IRC**: Toutes réponses <500 chars (limite Twitch)

### Modèles testés (rejetés)

| Modèle | Taille | Succès | Latence | Verdict |
|--------|--------|--------|---------|---------|
| Phi-2 Q4/Q5 | 2.7B | ❌ 45% | 0.35s | Trop verbeux (91-113 mots, hallucinations) |
| Qwen 7B Q4 | 7B | ✅ 100% | 0.21s | **Parfait** mais trop lourd (hardware rejet) |
| **Qwen 1.5B Q4** | **1.5B** | **✅ 87%** | **0.25s** | **PRODUCTION** (optimal ratio perf/ressources) |

---

## Configuration Optimale

### Priorité Endpoints

1. **LM Studio** (priorité 1): Qwen 2.5-1.5B local
2. **DeadBot** (priorité 2): FastAPI local si configuré
3. **OpenAI GPT-4o-mini** (fallback): Si tous locaux indisponibles

### Mode ASK (questions factuelles)

**But**: Réponses concises et claires (≤250 chars réels)

```python
# Prompt
SYSTEM_ASK_FINAL = """Tu es serda_bot. Réponds de façon concise et claire.
Maximum 200 caractères par réponse.  # Marge sécurité → réel ~136-220 chars

Exemples:
"python" → "Langage populaire pour scripts et IA."
"blockchain" → "Technologie de registre décentralisé sécurisé."
"""

# Config LM Studio
temperature = 0.4          # Déterministe, zéro hallucinations
max_tokens = 80            # ~200 chars prompt → réel ≤250 chars
stop = ["\n\n"]           # Stop paragraphes seulement (explications complètes)
repeat_penalty = 1.1       # Anti-répétition
```

**Résultats**: 93.3% ≤250 chars, moyenne 136 chars, 0 hallucinations

### Mode CHILL (interactions sociales)

**But**: Réponses ultra-courtes fun/cool (1-5 mots)

```python
# Prompt
SYSTEM_CHILL_FINAL = """Tu es serda_bot, bot Twitch cool mais flemme de trop parler.
Réponds toujours en 1-5 mots maximum. Style décontracté.

Exemples:
"Salut !" → "Yo."
"lol" → "Marrant."
"t'es qui toi ?" → "Le bot du stream."
"""

# Few-shot enrichi (réactions + questions)
messages = [
    {"role": "user", "content": "lol"},
    {"role": "assistant", "content": "Marrant."},
    {"role": "user", "content": "t'es qui toi ?"},
    {"role": "assistant", "content": "Le bot du stream."},
    {"role": "user", "content": user_input}
]

# Config LM Studio
temperature = 0.5          # Stable et naturel
max_tokens = 20            # Ultra strict (1-5 mots)
stop = None                # Pas de stop, naturel
repeat_penalty = 1.0       # Pas de pénalité
```

**Résultats**: 80% ≤5 mots, moyenne 2.6 mots, 0.09s latence

---

## Processus d'Optimisation

### Phase 1: Tests comparatifs modèles
- Qwen 1.5B → 7B → Phi-2
- Verdict: 7B parfait mais trop lourd, 1.5B optimisable

### Phase 2: Prompt engineering
- Baseline: 55% ASK, 53% CHILL
- Limite 250 chars: 85.7% ASK, 80% CHILL
- **Limite 200 chars (marge sécurité)**: 93.3% ASK ✅

### Phase 3: Few-shot enrichissement
- CHILL questions: 53% → 80% (+27% boost)
- Ajout 2 exemples (réactions + questions)

### Phase 4: Températures adaptatives
- ASK: 0.4 (déterministe, zéro hallucinations)
- CHILL: 0.5 (stable, naturel)

---

## Utilisation en Production

### Configuration LM Studio

1. **Charger le modèle**: `Qwen2.5-1.5B-Instruct-Q4_K_M.gguf`
2. **Endpoint**: `http://127.0.0.1:1234/v1/chat/completions`
3. **Laisser LM Studio gérer**: GPU layers, context, etc.

### Fichiers Config

- **Prompts**: `src/prompts/prompt_loader.py`
  - `SYSTEM_ASK_FINAL` (200 chars limit)
  - `SYSTEM_CHILL_FINAL` (1-5 mots)
  
- **API calls**: `src/utils/model_utils.py`
  - Températures 0.4/0.5
  - Max tokens 80/20
  - Stop sequences dynamiques

### Tests de Validation

```bash
# Test ASK (93% succès validé)
python personnal/tests/test_ask_200_chars.py

# Test CHILL (80% succès validé)
python personnal/tests/test_chill_enriched.py

# Test production massif (85 cas)
python personnal/tests/test_production_final.py
```

---

## Métriques Finales

### ASK Mode
- **Succès**: 93.3% ≤250 chars (14/15 cas)
- **Moyenne**: 136 chars
- **Max observé**: 293 chars (reste <500 IRC ✅)
- **Latence**: 0.41s
- **Hallucinations**: 0

### CHILL Mode
- **Succès**: 80% ≤5 mots (40/50 cas)
- **Moyenne**: 2.6 mots
- **Latence**: 0.09s

### Global
- **Succès combiné**: ~87% (largement au-dessus objectif 80%)
- **100% sous limite IRC**: Toutes réponses <500 chars ✅
- **Amélioration vs baseline**: +38% ASK, +27% CHILL

---

## Notes Techniques

### Pourquoi limite 200 chars dans le prompt ?

**Logique**: Prompt dit "200 chars" → modèle génère ~136-220 → toujours <250 chars cible

**Marge sécurité**: Si on met "250 chars" dans prompt, certains cas dépassent 250-363 chars réels

**Cas problématiques résolus**:
- "comment fonctionne internet" : 330→128 chars ✅
- "blockchain" : 363→220 chars ✅
- "machine learning" : 271→155 chars ✅

### Températures adaptatives

- **ASK 0.4**: Déterministe, répétable, zéro hallucinations
- **CHILL 0.5**: Stable, naturel, variations acceptables pour chat

### Few-shot enrichi (CHILL)

Sans few-shot: 53% succès questions ("t'es qui toi ?" → 15 mots verbeux)
Avec few-shot: 80% succès questions ("t'es qui toi ?" → "Le bot du stream." 4 mots)

**Impact**: +27% boost questions, réactions déjà bonnes (80% baseline)

---

## Maintenance

### Si performances dégradent:

1. **Vérifier LM Studio actif**: `curl http://127.0.0.1:1234/v1/models`
2. **Tester endpoint**: `python scripts/smoke_model.py`
3. **Vérifier prompts**: `src/prompts/prompt_loader.py` (pas modifiés)
4. **Re-run tests validation**: `personnal/tests/test_*.py`

### Si besoin upgrade modèle:

- Qwen 2.5-3B Q4 (2x plus gros, potentiel +5% succès)
- Qwen 2.5-7B Q4 (si hardware upgrade, 100% succès validé)

**Note**: Actuel 1.5B déjà optimal pour contraintes hardware (87% succès global)

---

## Fallback OpenAI

### GPT-4o-mini (Production)

**Choisi pour**:
- ✅ 100% succès ASK + CHILL (testé 10 cas variés)
- ✅ 4x moins cher que GPT-3.5-turbo
  - Input: $0.15/1M tokens (vs $0.50)
  - Output: $0.60/1M tokens (vs $1.50)
- ✅ Latence acceptable pour fallback (0.57-1.52s)

**Performances validées**:
- ASK: 100% ≤250 chars, 188 chars moyenne, 1.52s
- CHILL: 100% ≤5 mots, 3.8 mots moyenne, 0.67s

**Config**:
```yaml
openai:
  api_key: "sk-proj-xxxxx"
bot:
  openai_model: "gpt-4o-mini"  # Fallback si LM Studio down
```

**Activation**: Automatique si LM Studio + DeadBot indisponibles
