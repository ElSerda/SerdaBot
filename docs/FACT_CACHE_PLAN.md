# Fact Cache - Plan d'Implémentation

## 🎯 Objectif
Corriger les hallucinations du 1.5B en fournissant des faits vérifiés depuis des sources fiables (Wikipedia, Wikidata).

---

## 📋 TODO

### Phase 1 : Infrastructure de Base
- [ ] Créer `src/utils/fact_cache.py`
- [ ] Implémenter cache local JSON pour éviter trop d'API calls
- [ ] Définir structure cache : `{"query": str, "facts": str, "source": str, "timestamp": int}`
- [ ] TTL cache : 30 jours (facts changent peu)

### Phase 2 : Intégration Wikipedia
- [ ] API wrapper Wikipedia FR : `https://fr.wikipedia.org/api/rest_v1/page/summary/{title}`
- [ ] Extraire `extract` (résumé 200-300 chars)
- [ ] Normaliser query → Wikipedia title (fuzzy match)
- [ ] Fallback English si FR vide

### Phase 3 : Intégration Wikidata (Optionnel)
- [ ] SPARQL queries pour faits structurés
- [ ] Mapping entités → propriétés clés
- [ ] Exemple : "panda roux" → P31 (instance of), P141 (conservation status)

### Phase 4 : Détection Besoin Cache
- [ ] Analyser query : détection entités nommées
- [ ] Catégories prioritaires : animaux, tech, science, histoire
- [ ] Si match → inject fact dans system prompt ou remplace réponse

### Phase 5 : Mode Hybride
**Option A** : Inject fact dans prompt
```
SYSTEM: "Fait vérifié: Les pandas roux sont des mammifères..."
USER: "parle moi des pandas roux"
```

**Option B** : Remplace réponse si match exact
```python
if fact_cache.has("pandas roux"):
    return fact_cache.get("pandas roux")
else:
    return model_response
```

**Option C** : Enrichissement post-génération
```python
response = model.generate()
facts = fact_cache.check(response)
if facts.hallucination_detected:
    return facts.verified_version
```

### Phase 6 : Testing
- [ ] Test unitaires cache
- [ ] Test intégration Wikipedia API
- [ ] Benchmark : latency impact (< 100ms acceptable)
- [ ] Validation qualité : 10 queries test

---

## 🛠️ APIs Candidates

### Wikipedia REST API
```bash
curl https://fr.wikipedia.org/api/rest_v1/page/summary/Petit_panda
```
**Pros** : Simple, rapide, résumés parfaits  
**Cons** : Nécessite titre exact

### Wikidata SPARQL
```sparql
SELECT ?item ?itemLabel ?desc WHERE {
  ?item rdfs:label "panda roux"@fr.
  ?item schema:description ?desc.
  FILTER(LANG(?desc) = "fr")
}
```
**Pros** : Données structurées, multilingue  
**Cons** : Plus complexe, requêtes plus lentes

### DBpedia (Fallback)
**Pros** : RDF, compatible SPARQL  
**Cons** : Données parfois obsolètes

---

## 📦 Structure Code Prévue

```
src/utils/fact_cache.py
├── FactCache (class)
│   ├── __init__(cache_file: str, ttl: int)
│   ├── get(query: str) -> Optional[str]
│   ├── set(query: str, facts: str, source: str)
│   ├── has(query: str) -> bool
│   └── cleanup_expired()
│
├── WikipediaClient (class)
│   ├── search(query: str) -> Optional[str]
│   ├── get_summary(title: str) -> str
│   └── normalize_title(query: str) -> str
│
└── inject_facts(prompt: str, query: str, cache: FactCache) -> str
```

**Usage** :
```python
from src.utils.fact_cache import FactCache, inject_facts

cache = FactCache("data/fact_cache.json", ttl=30*24*3600)

# Dans ask_command.py
prompt = "parle moi des pandas roux"
enriched_prompt = inject_facts(prompt, query=prompt, cache=cache)
# → Ajoute fact Wikipedia dans system prompt si trouvé
```

---

## ⚠️ Considérations

### Latency
- Cache hit : ~1ms
- Cache miss + Wikipedia API : ~200-500ms
- **Solution** : Async pre-fetch queries fréquentes

### Fraîcheur Données
- Wikipedia change peu (TTL 30j OK)
- Sujets tech : peut être obsolète (Python versions, etc.)
- **Solution** : TTL adaptatif par catégorie

### Privacy
- Pas de données user loggées
- Queries fact_cache anonymes
- OK RGPD

### Coût
- Wikipedia API : Gratuit, rate limit 200 req/s
- Wikidata SPARQL : Gratuit, rate limit 60 req/s
- **Solution** : Respecter rate limits, cache agressif

---

## 🎯 Critères de Succès

1. **Réduction hallucinations** : -80% sur animaux/tech/science
2. **Latency acceptable** : <200ms P95 avec cache
3. **Hit rate** : >70% sur queries ASK fréquentes
4. **Qualité** : Validation humaine 10 queries → 9/10 correctes

---

## 📅 Timeline Estimé

- **Semaine 1** : Infrastructure + cache local
- **Semaine 2** : Wikipedia API + tests
- **Semaine 3** : Intégration ask_command + monitoring
- **Semaine 4** : Optimisation + pre-fetch queries populaires

**Total** : ~1 mois pour fact_cache robuste

---

## 🔗 Ressources

- [Wikipedia API Docs](https://www.mediawiki.org/wiki/API:Main_page)
- [Wikidata SPARQL](https://query.wikidata.org/)
- [DBpedia Lookup](https://lookup.dbpedia.org/)
