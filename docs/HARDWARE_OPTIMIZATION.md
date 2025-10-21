# 🔧 Hardware Optimization Guide

Guide d'optimisation du SerdaBot pour différentes configurations matérielles.

---

## 📊 Benchmarks de référence

### RTX 3080 (10GB VRAM) - Configuration de développement

**Setup testé :**
```yaml
max_tokens_chill: 100
temperature_chill: 0.8
max_messages_per_user: 12
model_timeout: 10s
KV offload: ON
GPU layers: ALL (33/33)
```

**Résultats (4 users × 10 messages) :**
- ⏱️ Latence moyenne : **980ms**
- 🚀 Throughput : **3.87 msg/s**
- 📈 Min/Max : 520ms / 1318ms
- ✅ Contexte max : ~180 tokens input

**Avec KV offload désactivé (❌ NE PAS FAIRE) :**
- ⏱️ Latence moyenne : **1763ms** (+80%)
- 🚀 Throughput : **2.16 msg/s** (-44%)
- ⚠️ Dégradation critique avec contexte croissant

---

## 🎯 GTX 780 (3GB VRAM) + CPU Fallback - Configuration production

### ⚙️ Configuration recommandée

**LM Studio / llama.cpp :**
```
Model: Qwen2.5-3B-Instruct-Q4_K_M.gguf
GPU Layers: 20-25 (limite VRAM 3GB)
KV Cache: VRAM (CRITIQUE !)
Context: 2048 tokens
Flash Attention: OFF (pas supporté sur Kepler)
```

**config.yaml :**
```yaml
bot:
  max_tokens_chill: 100        # Évite troncatures
  temperature_chill: 0.8       # Diversité réponses
  model_timeout: 10            # Généreux pour CPU fallback

rate_limiting:
  max_concurrent_users: 4      # Limite charge parallèle
  max_messages_per_user: 12    # Contexte maîtrisé (~180 tokens)
  max_idle_time: 3600          # Nettoyage mémoire
```

### 📈 Performances attendues

**Avec KV offload ON (✅ OBLIGATOIRE) :**
- Latence GPU (layers 0-20) : **3-5s**
- Latence CPU fallback : **4-8s**
- Throughput : **0.8-1.2 msg/s** (4 users)
- ✅ Dans le timeout de 10s

**Sans KV offload (💀 MORT DU BOT) :**
- Latence : **6-10s** (recalcul complet à chaque token)
- Risque timeout : **élevé**
- Utilisation CPU : **100%** (chauffe excessive)
- ❌ Non viable en production

### 🧠 Pourquoi KV offload est CRITIQUE

Le **KV cache** (Key-Value cache) stocke les embeddings des tokens du contexte :
- **Avec KV cache** : Le modèle réutilise les calculs précédents
- **Sans KV cache** : Recalcul complet à chaque nouveau token

**Impact sur GTX 780 :**
```
Contexte 180 tokens × 4 users parallèles = 720 tokens à traiter
Sans KV cache : 720 tokens recalculés à CHAQUE réponse = 💀
Avec KV cache : Seulement les nouveaux tokens = ✅
```

**Répartition mémoire optimale :**
```
VRAM 3GB :
├─ Modèle (layers 0-20) : ~2.2GB
├─ KV cache (prioritaire) : ~0.6GB
└─ Overhead système : ~0.2GB

Reste (layers 21-33) → CPU (10700K)
```

---

## 💻 CPU-Only Fallback (10700K sans GPU)

**Si GPU indisponible ou surchargé :**

**Setup :**
```
GPU Layers: 0 (full CPU)
Threads: 8 (10700K = 8c/16t)
KV offload: N/A (tout en RAM)
```

**Performances attendues :**
- ⏱️ Latence : **4-8s** (acceptable avec timeout 10s)
- 🚀 Throughput : **0.5-0.8 msg/s**
- 💾 RAM : ~4GB (modèle + contexte)

**Optimisations CPU :**
- Utilise `Q4_K_M` (pas Q5 ou Q6 = trop lent)
- Active `mmap` (chargement lazy du modèle)
- Limite `n_threads` à 8 (hyperthreading inutile pour inférence)

---

## 🔥 Comparaison Hardware

| GPU | VRAM | Layers | Latence (avg) | Throughput | KV Offload | Production |
|-----|------|--------|---------------|------------|------------|------------|
| **RTX 3080** | 10GB | 33/33 | 980ms | 3.87 msg/s | ON | ✅ Excellent |
| **GTX 780** | 3GB | 20-25 | 3-5s | 0.8-1.2 msg/s | **ON (CRITIQUE)** | ✅ Viable |
| **CPU 10700K** | - | 0 | 4-8s | 0.5-0.8 msg/s | N/A | ⚠️ Acceptable |
| **GTX 780** | 3GB | 20-25 | 6-10s | 0.3-0.5 msg/s | ❌ OFF | 💀 Non viable |

---

## 📝 Checklist de déploiement GTX 780

Avant de lancer le bot en prod sur matériel limité :

### ✅ Configuration LM Studio / llama.cpp
- [ ] Model : `Qwen2.5-3B-Instruct-Q4_K_M.gguf`
- [ ] GPU Layers : 20-25 (tester limite VRAM)
- [ ] **KV Cache Offload : ON** (CRITIQUE)
- [ ] Context : 2048 tokens
- [ ] Flash Attention : OFF

### ✅ Configuration bot (config.yaml)
- [ ] `max_tokens_chill: 100`
- [ ] `temperature_chill: 0.8`
- [ ] `model_timeout: 10`
- [ ] `max_concurrent_users: 4`
- [ ] `max_messages_per_user: 12`

### ✅ Tests de performance
```bash
# Test benchmark avec params production
python3 scripts/benchmark_conversation_manager.py --messages 10

# Vérifier :
# - Latence moyenne < 6s (idéal < 5s)
# - Aucun timeout (< 10s)
# - Historique limité à 12 messages
# - Pas de memory leak (plusieurs runs)
```

### ✅ Monitoring en prod
```bash
# Logue les latences élevées
tail -f logs/bot.log | grep "⏱️"

# Surveille RAM/VRAM
watch -n 2 nvidia-smi
htop
```

---

## 🎯 Optimisations avancées

### 1. Cache de réponses fréquentes

Le bot dispose déjà d'un cache RAM pour les facts :
- Questions fréquentes → 0ms latence
- Économise 90% de la charge sur "C'est quoi Python ?"

**Extension recommandée :**
```python
# Cache 10 questions les plus fréquentes
FREQUENT_QA = {
    "c'est quoi python": "Python ? Le langage qui me permet d'exister ! 🐍",
    "explique tuple": "Un tuple, c'est une liste qui refuse de changer ! 📦",
    # ...
}
```

### 2. Fallback conversationnel

Si latence > 5s, envoyer un message temporaire :
```python
if latency > 5.0:
    await send("Mon cerveau compile… Réessaie dans 2 sec ? ⏳")
```

### 3. Diversification des prompts

Le modèle répète "Évidemment, t'es pas la première…" → variantes :
```python
PROMPT_PREFIXES = [
    "Bien sûr",
    "Évidemment",
    "Sans problème",
    "Laisse-moi t'expliquer"
]
prefix = random.choice(PROMPT_PREFIXES)
```

### 4. Post-processing des troncatures

Si code Python tronqué, compléter automatiquement :
```python
def fix_truncated_code(response: str) -> str:
    if "print(" in response and not response.count("(") == response.count(")"):
        return response + ")"
    return response
```

---

## 🚨 Troubleshooting

### Problème : Latence > 10s (timeouts fréquents)

**Causes possibles :**
1. ❌ KV offload désactivé → **ACTIVER IMMÉDIATEMENT**
2. Trop de GPU layers → Réduire à 15-20
3. Contexte trop grand → Vérifier `max_messages_per_user`

**Solutions :**
```bash
# Test avec KV offload ON
# Réduire GPU layers si OOM
# Réduire max_messages à 8 si nécessaire
```

### Problème : Réponses tronquées

**Cause :** `max_tokens_chill` trop bas

**Solution :**
```yaml
max_tokens_chill: 100  # était 60, augmenté
```

### Problème : Réponses répétitives

**Cause :** `temperature` trop basse

**Solution :**
```yaml
temperature_chill: 0.8  # était 0.7, augmenté
```

### Problème : VRAM Out of Memory

**Cause :** Trop de GPU layers ou KV cache trop grand

**Solution :**
```
# Réduire GPU layers progressivement
GPU Layers: 25 → 20 → 15
# Ou réduire contexte
max_messages_per_user: 12 → 8
```

---

## 📚 Références

- **Benchmark scripts :** `scripts/benchmark_conversation_manager.py`
- **Configuration :** `src/config/config.yaml`
- **ConversationManager :** `src/utils/conversation_manager.py`
- **Model utils :** `src/utils/model_utils.py`

---

## 🎉 TL;DR

**Pour GTX 780 + CPU :**
1. ✅ KV offload **ON** (non négociable)
2. ✅ max_tokens_chill = 100
3. ✅ GPU layers = 20-25
4. ✅ max_messages = 12
5. ✅ timeout = 10s

**Résultat attendu :** 3-5s latence, stable, production-ready sur hardware 2013 🚀

---

*Dernière mise à jour : 2025-10-21*  
*Testé avec : Qwen2.5-3B-Instruct-Q4_K_M, RTX 3080, GTX 780, i7-10700K*
