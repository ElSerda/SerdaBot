# 🧪 Tests !trad - Quick Run Script

## 🚀 Installation Dependencies

```bash
# Install test dependencies
pip install pytest pytest-asyncio aiohttp

# Ou si dans venv
source kissbot-venv/bin/activate  # Linux
# kissbot-venv\Scripts\activate   # Windows
pip install pytest pytest-asyncio aiohttp
```

## 🎯 Run Tests

### Tests Unitaires (Mock)
```bash
# Run all translation tests
pytest test_translation.py -v

# Run specific language tests
pytest test_translation.py::TestTranslationCommand::test_trad_english_to_french -v
pytest test_translation.py::TestTranslationCommand::test_trad_spanish_to_french -v
pytest test_translation.py::TestTranslationCommand::test_trad_japanese_to_french -v

# Run error handling tests
pytest test_translation.py::TestTranslationCommand::test_trad_api_error_500 -v
pytest test_translation.py::TestTranslationCommand::test_trad_rate_limited -v
```

### Tests Intégration (Real API)
```bash
# Real Google API tests (optionnel)
pytest test_translation.py -m integration -v
```

## 📊 Expected Results

### ✅ Success Tests
```
test_trad_english_to_french ✓    - "Hello world" → "🌍 Bonjour le monde"
test_trad_spanish_to_french ✓    - "¿Cómo estás?" → "🌍 Comment ça va ?"
test_trad_german_to_french ✓     - "Guten Tag" → "🌍 Bonjour"
test_trad_japanese_to_french ✓   - "こんにちは" → "🌍 Bonjour"
test_trad_italian_to_french ✓    - "Ciao bella" → "🌍 Salut beauté"
test_trad_complex_sentence ✓     - Long sentence handling
```

### 🛡️ Error Handling Tests
```
test_trad_no_text_provided ✓     - "Usage: !trad <texte>"
test_trad_rate_limited ✓         - "Cooldown! Attends 3.2s"
test_trad_api_error_500 ✓        - "❌ Erreur traduction"
test_trad_network_exception ✓    - Exception handling
```

### 🔧 Integration Tests
```
test_real_google_translate_english ✓  - Real API call EN→FR
test_real_google_translate_spanish ✓  - Real API call ES→FR
```

## 🎮 Manual Test Commands

```bash
# Test en live dans le chat
!trad Hello world
!trad ¿Cómo estás?
!trad Guten Tag
!trad こんにちは
!trad Ciao bella
!trad How are you doing today?
```

## 📋 Test Coverage

- ✅ **Multi-languages**: EN, ES, DE, JP, IT → FR
- ✅ **Rate limiting**: Cooldown handling
- ✅ **Error cases**: API errors, network issues
- ✅ **Input validation**: Empty text handling
- ✅ **Google API**: Params validation
- ✅ **Real integration**: Optional live API tests