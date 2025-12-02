# SourceInfo API - Quick Start Guide

## 🚀 Start the API in 3 Steps

### 1. Install Dependencies (one-time setup)

```bash
# From the SourceInfo directory
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Start the Server

```bash
./run_api.sh
```

The API will start at **http://localhost:8000**

### 3. Try It Out!

Open your browser and visit:
- **Interactive Docs**: http://localhost:8000/docs
- **API Documentation**: http://localhost:8000/redoc

---

## 📝 Quick Examples

### Example 1: Analyze a News Article

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.nytimes.com/2024/article",
    "include_counternarratives": true
  }'
```

**Response**: Source info + credible right-leaning counternarratives

---

### Example 2: Get Source Information

```bash
curl http://localhost:8000/api/sources/nytimes.com
```

**Response**: Full NewsGuard rating, political lean, description

---

### Example 3: Find Counternarratives

```bash
curl http://localhost:8000/api/sources/nytimes.com/counternarratives?limit=5
```

**Response**: 5 high-credibility opposite-lean sources

---

### Example 4: Filter Sources

```bash
# Get all Center sources with high credibility
curl "http://localhost:8000/api/sources?lean=0&min_credibility=80"

# Get all fact-checkers
curl "http://localhost:8000/api/sources?source_type=fact_check"
```

---

### Example 5: Batch Analyze URLs

```bash
curl -X POST http://localhost:8000/api/analyze/batch \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://www.nytimes.com/article1",
      "https://www.wsj.com/article2",
      "https://www.bbc.com/article3"
    ]
  }'
```

---

## 💡 Use Cases

### Trump Admin Tracker
```python
import requests

response = requests.post("http://localhost:8000/api/analyze", json={
    "url": "https://www.washingtonpost.com/trump-article",
    "include_counternarratives": True,
    "preferred_leans": [1, 2]  # Right-leaning sources
})

source = response.json()["source"]
counters = response.json()["counternarratives"]
```

### Claim Analysis Tool
```python
# Score sources for evidence quality
response = requests.post("http://localhost:8000/api/sources/score", json={
    "domain": "factcheck.org",
    "context": {
        "claim_type": "political",
        "evidence_role": "support",
        "preferred_credibility": "high"
    }
})

score = response.json()["weighted_score"]
recommendation = response.json()["recommendation"]
```

---

## 📊 Current Database

- **222 total sources**
- **95 with NewsGuard ratings**
- **143 with political lean data**
- **17 fact-checkers**
- International coverage (Asia, Europe, Latin America, Africa)
- Specialized verticals (tech, business, science, sports)

---

## 📚 Full Documentation

See **README_API.md** for:
- Complete endpoint reference
- Weighted scoring algorithm
- Integration examples
- Configuration options

---

## 🔧 Troubleshooting

**Port already in use?**
```bash
# Change port in .env file
API_PORT=8001
```

**Database not found?**
```bash
# Check path in .env
DB_PATH=/full/path/to/sources.db
```

**Dependencies missing?**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

---

## ✅ Tests Passed

All core components tested and working:
- ✓ URL Parser (handles subdomains, mobile sites, bare domains)
- ✓ Database Queries (lookup, counternarratives, filtering, stats)
- ✓ Weighted Scoring (context-aware evidence quality assessment)

**Next Steps**: Start the server and try the interactive docs at http://localhost:8000/docs
