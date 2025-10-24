# 📋 Plan de Réorganisation KissBot

**Date** : 23 Octobre 2025  
**Objectif** : Refactoring modulaire (Phase 1) avant migration TwitchIO v3 (Phase 2)

---

## 🎯 **Architecture Cible (3 Piliers Distincts)**

### **Vision : 3 Parties Indépendantes**
```
1️⃣ Commandes Code Python/C++ (pur code, pas d'IA)
2️⃣ Intelligence LLM/API Cloud (commandes + events IA)
3️⃣ Events API Twitch (follow, sub, raid, modo)
```

### **Structure Fichiers**
```
KissBot/
├── main.py                  # Entry point (40 lignes)
├── bot.py                   # Bot TwitchIO core + Dispatcher (120 lignes)
│
├── 1️⃣ commands/            # Commandes PUR CODE (pas d'IA)
│   ├── __init__.py
│   ├── game_commands.py     # GameCommands (!game) - Python pur (~60 lignes)
│   └── utils_commands.py    # UtilsCommands (!ping, !stats, !help) - Python pur (~50 lignes)
│
├── 2️⃣ intelligence/        # 🆕 TOUT ce qui touche LLM/IA (isolé !)
│   ├── __init__.py
│   ├── commands.py          # LLM Commands (!ask) (~60 lignes)
│   ├── events.py            # LLM Events (@mention) (~60 lignes)
│   └── handler.py           # LLM Backend (local/OpenAI/cascade) (~220 lignes)
│
├── 3️⃣ twitch/              # 🆕 TOUT ce qui touche API Twitch
│   ├── __init__.py
│   └── events.py            # Phase 2 : on_follow, on_sub, on_raid (~100 lignes)
│
├── backends/                # 🆕 Backends métier (game APIs, cache)
│   ├── __init__.py
│   ├── game_lookup.py       # Game APIs fusion (350 lignes)
│   └── game_cache.py        # Game cache (120 lignes)
│
├── core/                    # Core utilities transverses
│   ├── __init__.py
│   ├── rate_limiter.py      # RateLimiter (40 lignes)
│   └── cache.py             # CacheManager générique (50 lignes)
│
├── tests/                   # 🧪 Tests unitaires (structure miroir)
│   ├── __init__.py
│   ├── test_bot.py          # Tests bot core + dispatcher
│   ├── commands/
│   │   ├── test_game_commands.py
│   │   └── test_utils_commands.py
│   ├── intelligence/
│   │   ├── test_commands.py
│   │   ├── test_events.py
│   │   └── test_handler.py
│   ├── twitch/
│   │   └── test_events.py
│   ├── backends/
│   │   ├── test_game_lookup.py
│   │   └── test_game_cache.py
│   └── core/
│       ├── test_rate_limiter.py
│       └── test_cache.py
│
├── config.yaml
├── requirements.txt
└── requirements-dev.txt     # pytest, pytest-asyncio, etc.
```

**Total : 28 fichiers (14 code + 14 tests), 11 dossiers, ~1210 lignes code + ~600 lignes tests**

### **Avantages Architecture 3 Piliers + Tests :**
✅ **Séparation TOTALE** : Code pur / LLM-IA / API Twitch = 3 dossiers distincts  
✅ **Isolation LLM/Cloud** : Tout dans `intelligence/` (facile à remplacer/désactiver)  
✅ **Isolation Twitch API** : Tout dans `twitch/` (migration v3 isolée)  
✅ **Zero duplication** : Handlers partagés via `bot.backends`  
✅ **Fork C++ ready** : `commands/` et `backends/` peuvent être recompilés  
✅ **bot.py ultra-lean** : Juste dispatcher entre les 3 piliers  
✅ **Maintenabilité** : Modifier LLM ? Juste `intelligence/`. Modifier Twitch ? Juste `twitch/`  
✅ **Debug ready** : Tests unitaires miroir = Tests ciblés en < 10 secondes  
✅ **CI/CD ready** : Structure pytest standard pour GitHub Actions

---

## 🔄 **Mapping de Migration**

### **Fichiers à Migrer**

| Fichier Actuel | Nouveau Chemin | Action |
|---------------|---------------|--------|
| `local_llm.py` | `llm/handler.py` | Renommer + Déplacer |
| `game_lookup.py` | `game/lookup.py` | Renommer + Déplacer |
| `game_cache.py` | `game/cache.py` | Déplacer |
| `cache.py` (RateLimiter) | `core/rate_limiter.py` | **Split** + Déplacer |
| `cache.py` (CacheManager) | `core/cache.py` | **Split** + Déplacer |
| `bot.py` | `bot.py` | **Update imports** |
| `main.py` | `main.py` | Garder tel quel ✅ |

### **Fichiers à Créer (Structure 3 Piliers)**

| Nouveau Fichier | Contenu | Pilier |
|----------------|---------|--------|
| `commands/__init__.py` | Exports components code pur | 1️⃣ Code Pur |
| `commands/game_commands.py` | `GameCommands(Component)` avec `!game` | 1️⃣ Code Pur |
| `commands/utils_commands.py` | `UtilsCommands(Component)` avec `!ping`, `!stats`, `!help` | 1️⃣ Code Pur |
| `intelligence/__init__.py` | Exports LLM components + handler | 2️⃣ LLM/IA |
| `intelligence/commands.py` | `LLMCommands(Component)` avec `!ask` | 2️⃣ LLM/IA |
| `intelligence/events.py` | `handle_mention()` → LLM sur `@KissBot` | 2️⃣ LLM/IA |
| `intelligence/handler.py` | `LLMHandler` (cascade local/OpenAI/fallbacks) | 2️⃣ LLM/IA |
| `twitch/__init__.py` | Exports Twitch events | 3️⃣ API Twitch |
| `twitch/events.py` | Skeleton Phase 2 : `on_follow`, `on_sub`, `on_raid` | 3️⃣ API Twitch |
| `backends/__init__.py` | Exports game APIs | Backend |
| `backends/game_lookup.py` | `GameLookup` (RAWG + Steam APIs) | Backend |
| `backends/game_cache.py` | `GameCache` (cache jeux) | Backend |
| `core/__init__.py` | Exports utils transverses | Core |
| `core/rate_limiter.py` | `RateLimiter` | Core |
| `core/cache.py` | `CacheManager` générique | Core |

---

## 📊 **Inventaire par Pilier**

### **1️⃣ Commandes Code Pur (Python/C++)**
- ✅ `!game <name>` → `commands/game_commands.py` → `backends/game_lookup.py`
- ✅ `!ping` → `commands/utils_commands.py` (logique simple)
- ✅ `!stats` → `commands/utils_commands.py` (statistiques bot)
- ✅ `!help` → `commands/utils_commands.py` (liste commandes)
- ✅ `!cache` → `commands/utils_commands.py` (admin, debug cache)

**Caractéristiques** : Pas d'API externe, pas d'IA, juste du code local

### **2️⃣ Intelligence LLM/IA (API Cloud)**
- ✅ `!ask <question>` → `intelligence/commands.py` → `intelligence/handler.py`
- ✅ `@KissBot <message>` → `intelligence/events.py` → `intelligence/handler.py`
- ❌ ~~`!chill`~~ → **Supprimé** (remplacé par mentions)

**Caractéristiques** : LLM local (LM Studio) + Cloud (OpenAI) + Fallbacks

### **3️⃣ Events API Twitch (Phase 2)**
- ⏳ `on_follow(user)` → `twitch/events.py` (EventSub)
- ⏳ `on_subscribe(user)` → `twitch/events.py` (EventSub)
- ⏳ `on_raid(raider, viewers)` → `twitch/events.py` (EventSub)
- ⏳ `on_channel_points(reward)` → `twitch/events.py` (EventSub)

**Caractéristiques** : API Helix, OAuth2, EventSub websocket

### **Events TwitchIO v2 (dans bot.py - Core uniquement)**
- ✅ `event_ready` → Bot lifecycle (connexion, welcome message)
- ✅ `event_message` → Dispatch vers `events/llm_events.py` si mention
- ✅ `event_command_error` → Error handling
- ✅ `setup_hook` → Charge handlers + components

### **Events API Twitch (Phase 2 TwitchIO v3)**
- ⏳ `event_follow` → `events/twitch_events.py` (EventSub)
- ⏳ `event_subscribe` → `events/twitch_events.py` (EventSub)
- ⏳ `event_raid` → `events/twitch_events.py` (EventSub)

### **Handlers Backend (modules)**
- ✅ `LLMHandler` → `llm/handler.py` (cascade local/OpenAI/fallbacks)
- ✅ `GameLookup` → `game/lookup.py` (RAWG + Steam APIs)
- ✅ `GameCache` → `game/cache.py` (cache jeux avec TTL)
- ✅ `RateLimiter` → `core/rate_limiter.py` (rate limiting per-user)
- ✅ `CacheManager` → `core/cache.py` (cache générique)

---

## 🚀 **Plan d'Exécution Phase 1**

### **Étape 1 : Créer Structure 3 Piliers**
```bash
mkdir -p commands intelligence twitch backends core
touch commands/__init__.py intelligence/__init__.py twitch/__init__.py backends/__init__.py core/__init__.py
```

### **Étape 2 : Migrer Fichiers (3 Piliers)**
```bash
# 2️⃣ Intelligence (LLM/IA)
mv local_llm.py intelligence/handler.py

# Backends (Game APIs)
mv game_lookup.py backends/game_lookup.py
mv game_cache.py backends/game_cache.py
```

### **Étape 3 : Split cache.py**
```python
# Extraire RateLimiter → core/rate_limiter.py
# Extraire CacheManager → core/cache.py
```

### **Étape 4 : Créer Components & Events (3 Piliers)**
```python
# 1️⃣ commands/game_commands.py (Code pur Python)
from twitchio.ext import commands

class GameCommands(commands.Component):
    @commands.command(name='game')
    async def cmd_game(self, ctx, *, game_name: str):
        # Recherche jeu via backends
        game_info = await self.bot.game_lookup.search_game(game_name)
        await ctx.send(f"🎮 {game_info.name} ...")

# 2️⃣ intelligence/commands.py (LLM/IA)
from twitchio.ext import commands

class LLMCommands(commands.Component):
    @commands.command(name='ask')
    async def cmd_ask(self, ctx, *, question: str):
        # Questions factuelles avec LLM
        response = await self.bot.llm_handler.generate_response(
            question, context="ask", user_name=ctx.author.name
        )
        await ctx.send(response)

# 2️⃣ intelligence/events.py (Mentions → IA)
async def handle_mention(bot, message):
    """Trigger LLM quand le bot est mentionné."""
    clean_msg = message.content.replace(f"@{bot.nick}", "").strip()
    response = await bot.llm_handler.generate_response(
        clean_msg, context="mention", user_name=message.author.name
    )
    await message.channel.send(f"@{message.author.name} {response}")

# 3️⃣ twitch/events.py (API Twitch Phase 2)
async def on_follow(bot, user):
    """EventSub : Nouveau follower."""
    # TODO: Phase 2
    pass
```

### **Étape 5 : Update bot.py (Dispatcher 3 Piliers)**
```python
# bot.py - Architecture 3 Piliers Distincts
from commands import GameCommands, UtilsCommands
from intelligence.commands import LLMCommands
from intelligence.events import handle_mention
from intelligence.handler import LLMHandler
from backends.game_lookup import GameLookup

class KissBot(commands.Bot):
    async def setup_hook(self):
        # Backends partagés
        self.rate_limiter = RateLimiter()
        
        # 1️⃣ Backends Code Pur
        self.game_lookup = GameLookup(self.config)
        
        # 2️⃣ Backend Intelligence (LLM/IA)
        self.llm_handler = LLMHandler(self.config)
        
        # Charger components
        await self.add_component(GameCommands())      # 1️⃣ Code pur
        await self.add_component(UtilsCommands())     # 1️⃣ Code pur
        await self.add_component(LLMCommands())       # 2️⃣ Intelligence
    
    async def event_ready(self):
        """Bot connecté."""
        self.logger.info(f"✅ {self.nick} connecté")
    
    async def event_message(self, message):
        """Dispatcher 3 piliers : Code / IA / Twitch."""
        if message.echo:
            return
        
        # 1️⃣ Commandes code pur (!game, !ping, etc.)
        await self.handle_commands(message)
        
        # 2️⃣ Intelligence : Mention → LLM
        if self.nick.lower() in message.content.lower():
            await handle_mention(self, message)
        
        # 3️⃣ Phase 2 : Events Twitch API (TODO)
```

### **Étape 5 : Créer Events Skeleton**
```python
# events/handlers.py
"""
Event handlers Twitch API Helix (Phase 2 TwitchIO v3)
TODO: Implémenter on_follow, on_subscribe, on_raid après migration v3
"""
```

### **Étape 6 : Créer Structure Tests**
```bash
mkdir -p tests/commands tests/intelligence tests/twitch tests/backends tests/core
touch tests/__init__.py tests/test_bot.py
touch tests/commands/test_game_commands.py tests/commands/test_utils_commands.py
touch tests/intelligence/test_commands.py tests/intelligence/test_events.py tests/intelligence/test_handler.py
touch tests/twitch/test_events.py
touch tests/backends/test_game_lookup.py tests/backends/test_game_cache.py
touch tests/core/test_rate_limiter.py tests/core/test_cache.py

# Créer pytest.ini
cat > pytest.ini << 'EOF'
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
EOF

# Créer requirements-dev.txt
cat > requirements-dev.txt << 'EOF'
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-mock>=3.10.0
pytest-cov>=4.0.0
EOF
```

### **Étape 7 : Tester Architecture**
```bash
# Lancer tous les tests
pytest tests/ -v

# Tests ciblés par pilier
pytest tests/intelligence/ -v     # Juste LLM
pytest tests/backends/ -v         # Juste Game APIs
pytest tests/twitch/ -v           # Juste Events Twitch

# Tests fonctionnels bot
python main.py
!ask Qu'est-ce que Python ?     # → LLM command
@KissBot salut !                # → LLM event
!game Hades                     # → Game API
!stats                          # → Utils
```

---

## ✅ **Critères de Validation**

### **Structure**
- [ ] 6 dossiers créés : `commands/`, `intelligence/`, `twitch/`, `backends/`, `core/`, `tests/`
- [ ] 28 fichiers au total (14 code + 14 tests)
- [ ] Tous les `__init__.py` créés avec exports
- [ ] Components chargés dans `bot.py` via `setup_hook()`
- [ ] Structure tests miroir des modules
- [ ] `pytest.ini` et `requirements-dev.txt` configurés

### **Fonctionnalité**
- [ ] Bot démarre sans erreur
- [ ] `!ask` fonctionne (LLM)
- [ ] `!game` fonctionne (APIs)
- [ ] `!ping`, `!stats`, `!help` fonctionnent
- [ ] Rate limiting actif
- [ ] Cache jeux actif
- [ ] Tests unitaires passent (`pytest tests/ -v`)
- [ ] Coverage > 70% sur modules critiques

### **Code Quality**
- [ ] Imports propres (pas d'import circulaire)
- [ ] Pas de code dupliqué
- [ ] Logs fonctionnels
- [ ] Pas de régression

---

## 🔮 **Phase 2 (Future - TwitchIO v3)**

### **À Faire Plus Tard**
1. Upgrade `requirements.txt` → `twitchio==3.x`
2. Refactor `bot.py` pour TwitchIO v3 (OAuth2, client_id, etc.)
3. Implémenter `events/handlers.py` (on_follow, on_sub, etc.)
4. Ajouter config OAuth2 Helix dans `config.yaml`
5. Tester events natifs API Helix

---

## 📝 **Notes**

### **Pourquoi cette arbo avec Components ?**
- ✅ **Modulaire** : 1 component = 1 groupe de commandes logique
- ✅ **Zero duplication** : Handlers partagés (`self.bot.llm`, `self.bot.game_lookup`)
- ✅ **Évolutif** : Ajouter `MusicCommands` = créer 1 fichier + `add_component()`
- ✅ **Maintenable** : Code lisible, groupement clair
- ✅ **Pattern officiel** : Recommandé par TwitchIO v3
- ✅ **Pas d'usine à gaz** : 5 dossiers, logique directe

### **Ce qui reste dans bot.py (ultra-lean - 120 lignes !)**
- Classe `KissBot(commands.Bot)` (dispatcher 3 piliers)
- `setup_hook()` : Charge backends + components des 3 piliers
- `event_ready()` : Connexion bot
- `event_message()` : **Dispatcher** → 1️⃣ Commands / 2️⃣ LLM / 3️⃣ Twitch
- `event_command_error()` : Error handling

### **1️⃣ Pilier Code Pur (commands/ + backends/)**
- `commands/game_commands.py` : `!game` → APIs jeux
- `commands/utils_commands.py` : `!ping`, `!stats`, `!help`
- `backends/game_lookup.py` : RAWG + Steam APIs (Python pur)
- `backends/game_cache.py` : Cache jeux (Python pur)

**Caractéristique** : Pas d'API cloud, code local, peut être forké en C++

### **2️⃣ Pilier Intelligence (intelligence/)**
- `intelligence/commands.py` : `!ask` → Questions factuelles
- `intelligence/events.py` : `@KissBot` → Conversation
- `intelligence/handler.py` : LLM Backend (local + OpenAI + fallbacks)

**Caractéristique** : TOUT le LLM/IA isolé, facile à désactiver/remplacer

### **3️⃣ Pilier Twitch (twitch/)**
- `twitch/events.py` : Phase 2 → `on_follow`, `on_sub`, `on_raid`

**Caractéristique** : API Helix EventSub, migration v3 isolée

### **Core (utilitaires transverses)**
- `core/rate_limiter.py` : Rate limiting
- `core/cache.py` : Cache générique

---

**Prêt pour réorganisation !** 🚀
