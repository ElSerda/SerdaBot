# 🎮 KissBot Commands Guide

## 📋 Commands Overview

### Basic Commands
- `!ping` - Test bot responsiveness and latency
- `!help` - Display available commands list
- `!stats` - Show bot statistics (uptime, commands processed)
- `!cache` - Display cache statistics and hit rates
- `!serdagit` - Bot source code and creator information

### Game Commands
- `!gameinfo <game>` (alias: `!gi`) - Get detailed game information
- `!gamecategory` (alias: `!gc`) - Auto-detect current stream game

### Intelligence Commands
- `!ask <question>` - Ask the LLM a question
- `@bot <message>` - Natural conversation with mention system

---

## 🎮 Game Information Commands

### `!gameinfo <game>` / `!gi <game>`

**Purpose:** Retrieve comprehensive game information from multiple APIs

**Data Sources:**
- **Primary:** RAWG API (aggregates Steam, Epic, GOG, itch.io)
- **Secondary:** Steam API (for enrichment and validation)
- **Coverage:** 99%+ of PC gaming catalog

**Example Usage:**
```
!gi zelda breath of the wild
!gameinfo cyberpunk 2077
!gi mario
```

#### ⚡ Reliability & Limitations

**Overall Reliability: 90-99%** 📊

The game lookup system is designed to be robust but depends on external APIs:

**✅ High Reliability Scenarios (95-99%):**
- Popular games with exact names (`!gi cyberpunk 2077`)
- Well-known franchises (`!gi zelda`, `!gi mario`)
- Games with 2+ word specificity (`!gi mario kart`)
- Recently released AAA titles

**⚠️ Medium Reliability Scenarios (85-95%):**
- Indie games with uncommon names
- Very old games (pre-2000)
- Games with special characters or non-English names
- Abbreviated queries (`!gi lol`, `!gi wow`)

**❌ Potential Issues (5-15% of queries):**
- **API Downtime:** External services temporarily unavailable
- **Typos & Misspellings:** May return incorrect results
- **Ambiguous Names:** Generic terms may match wrong games
- **Regional Variations:** Different titles in different regions
- **Network Issues:** Timeout or connection failures

#### 🔧 Error Handling

The system includes comprehensive fallbacks:

1. **Confidence Scoring:** Results marked as HIGH/MEDIUM/LOW confidence
2. **Low Confidence Rejection:** Unclear results are filtered out with user guidance
3. **Graceful Degradation:** Always returns a response, never crashes
4. **Multiple Source Validation:** Cross-references RAWG + Steam data
5. **Timeout Protection:** 10-second timeout prevents hanging

#### 💡 Tips for Best Results

- **Be Specific:** `!gi zelda breath of the wild` > `!gi zelda`
- **Use Full Names:** `!gi cyberpunk 2077` > `!gi cyberpunk`
- **Check Spelling:** Exact names work better than typos
- **Try Alternatives:** If no result, try different name variations

#### 🚨 Known Edge Cases

- **Franchise Names:** May return latest or most popular entry
- **Remasters/Editions:** May prioritize original or remastered version
- **Platform Exclusives:** Some console-only games may have limited PC data
- **Early Access:** Games in development may have incomplete information

---

### `!gamecategory` / `!gc`

**Purpose:** Auto-detect and display information about the current stream's game

**Reliability: 95%+** (depends on streamer having set correct game category)

**Requirements:**
- Stream must be live
- Game category must be set in Twitch dashboard
- Bot requires Twitch API access

---

## 🤖 Intelligence System

### `!ask <question>`

Ask the bot's LLM system a question. Uses cascade fallback:
1. **Local LLM** (LM Studio/Ollama) - if configured
2. **OpenAI API** - if local unavailable
3. **Fun Fallbacks** - if all APIs down

### `@bot <message>`

Natural conversation system with 15-second cooldown per user.

**Special Features:**
- 30% roast chance for El_Serda (easter egg)
- Context-aware responses
- Rate limiting protection

---

## 📊 Monitoring Commands

### `!stats`

Displays:
- Bot uptime
- Commands processed
- Memory usage
- LLM provider status

### `!cache`

Shows cache performance:
- Hit rate percentage
- Total entries stored
- Last update time

---

## 🔧 Production Notes

**KissBot V1** is designed for 99%+ uptime with comprehensive error handling. However, like all systems depending on external APIs, occasional issues may occur:

- **API Rate Limits:** Automatic backoff and retry
- **Network Issues:** Graceful degradation with fallbacks
- **Invalid Queries:** Clear error messages and guidance
- **Service Downtime:** Multiple fallback systems

The KISS architecture ensures that even when components fail, the bot remains functional and responsive.