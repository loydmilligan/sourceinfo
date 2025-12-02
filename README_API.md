# SourceInfo API Documentation

## Overview

REST API for news source credibility assessment, bias detection, and counternarrative discovery.

**Current Version**: 0.1.0
**Base URL**: `http://localhost:8000`
**API Docs**: `http://localhost:8000/docs` (Swagger UI)
**Alternative Docs**: `http://localhost:8000/redoc`

## Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 2. Start the Server

```bash
# Option 1: Using the startup script
./run_api.sh

# Option 2: Direct uvicorn command
source .venv/bin/activate
python -m uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`

### 3. Test the API

Open your browser and navigate to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Or test with curl:

```bash
# Health check
curl http://localhost:8000/health

# Analyze a URL
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.nytimes.com/2024/article"}'
```

---

## API Endpoints

### Core Endpoints

#### 1. Analyze Article URL

**POST** `/api/analyze`

Analyze an article URL to get source information and counternarratives.

**Request Body**:
```json
{
  "url": "https://www.nytimes.com/2024/01/article-slug",
  "include_counternarratives": true,
  "min_counternarrative_credibility": 60,
  "counternarrative_limit": 10,
  "preferred_leans": [1, 2]
}
```

**Response**:
```json
{
  "url": "https://www.nytimes.com/2024/01/article-slug",
  "domain": "nytimes.com",
  "source_found": true,
  "source": {
    "domain": "nytimes.com",
    "name": "New York Times",
    "political_lean": -1,
    "political_lean_label": "Lean Left",
    "newsguard_score": 100,
    "newsguard_rating": "High Credibility",
    "source_type": "news_media",
    "description": "..."
  },
  "counternarratives": [
    {
      "domain": "wsj.com",
      "name": "Wall Street Journal",
      "political_lean": 1,
      "political_lean_label": "Lean Right",
      "newsguard_score": 100,
      "weighted_score": 100
    }
  ]
}
```

**Use Cases**:
- Trump Admin Tracker: Get bias info + counternarrative recommendations
- Claim Analysis: Assess source credibility for evidence
- Research: Understand source background

---

#### 2. Batch Analyze URLs

**POST** `/api/analyze/batch`

Analyze multiple URLs in a single request (max 50).

**Request Body**:
```json
{
  "urls": [
    "https://www.nytimes.com/article1",
    "https://www.wsj.com/article2",
    "https://www.bbc.com/news/article3"
  ],
  "options": {
    "include_counternarratives": true,
    "min_counternarrative_credibility": 60
  }
}
```

**Response**:
```json
{
  "results": [...],
  "total": 3,
  "successful": 3,
  "failed": 0
}
```

---

#### 3. Get Source by Domain

**GET** `/api/sources/{domain}`

Get detailed information about a specific source.

**Example**:
```bash
curl http://localhost:8000/api/sources/nytimes.com
```

---

#### 4. List/Filter Sources

**GET** `/api/sources`

Query sources with filters and pagination.

**Query Parameters**:
- `domains`: Comma-separated domains for bulk lookup
- `lean`: Political lean (-2 to 2)
- `min_credibility`: Minimum NewsGuard score
- `source_type`: Source type filter
- `limit`: Max results (default 100)
- `offset`: Pagination offset

**Examples**:
```bash
# Get all Center sources with high credibility
curl "http://localhost:8000/api/sources?lean=0&min_credibility=80"

# Get all fact-checkers
curl "http://localhost:8000/api/sources?source_type=fact_check"

# Bulk lookup
curl "http://localhost:8000/api/sources?domains=nytimes.com,wsj.com,bbc.com"
```

---

#### 5. Get Counternarratives

**GET** `/api/sources/{domain}/counternarratives`

Find credible sources from opposing political viewpoints.

**Query Parameters**:
- `min_credibility`: Minimum NewsGuard score (default 60)
- `limit`: Max results (default 10)
- `preferred_leans`: Comma-separated lean values (e.g., "1,2")

**Example**:
```bash
curl "http://localhost:8000/api/sources/nytimes.com/counternarratives?min_credibility=80&limit=5"
```

---

#### 6. Score Source for Evidence

**POST** `/api/sources/score`

Calculate weighted evidence quality score with context.

**Request Body**:
```json
{
  "domain": "nytimes.com",
  "context": {
    "claim_type": "political",
    "evidence_role": "support",
    "preferred_credibility": "high"
  }
}
```

**Response**:
```json
{
  "source": {...},
  "weighted_score": 95.0,
  "scoring_breakdown": {
    "credibility_score": 100,
    "bias_penalty": -5,
    "type_bonus": 0,
    "explanation": "High credibility Lean Left source; -5 penalty for bias"
  },
  "recommendation": "strong"
}
```

---

#### 7. Database Statistics

**GET** `/api/sources/stats/overview`

Get database statistics and distribution metrics.

**Response**:
```json
{
  "total_sources": 222,
  "with_newsguard": 95,
  "with_political_lean": 143,
  "lean_distribution": {
    "Left": 14,
    "Lean Left": 53,
    "Center": 42,
    "Lean Right": 18,
    "Right": 16
  },
  "type_distribution": {
    "news_media": 195,
    "fact_check": 17,
    "trade_publication": 6
  },
  "credibility_tiers": {
    "high": 75,
    "medium": 15,
    "low": 5
  }
}
```

---

## Weighted Scoring

The API uses context-aware scoring to assess source quality:

### Formula
```
weighted_score = base_credibility + type_bonus - bias_penalty
```

### Type Bonuses
- **Fact-checker**: +10 (universal)
- **Think tank**: +5 (for policy/economic claims)
- **Wire service**: +5 (for factual reporting)
- **Trade publication**: +3

### Bias Penalties (for neutral evidence only)
- **Left/Right** (±2): -10
- **Lean Left/Right** (±1): -5
- **Center** (0): 0

### Recommendations
- **Strong** (80-100): Highly recommended
- **Acceptable** (60-79): Usable with context
- **Use with caution** (40-59): Lower quality
- **Not recommended** (<40): Avoid

---

## Integration Examples

### Trump Admin Tracker

```python
import requests

# Analyze event source
response = requests.post("http://localhost:8000/api/analyze", json={
    "url": "https://www.nytimes.com/trump-corruption-article",
    "include_counternarratives": True,
    "min_counternarrative_credibility": 70,
    "preferred_leans": [1, 2]  # Right-leaning counternarratives
})

data = response.json()
source = data["source"]
counters = data["counternarratives"]

print(f"Source: {source['name']} ({source['political_lean_label']})")
print(f"Credibility: {source['newsguard_score']}/100")
print("\\nCounternarratives:")
for c in counters:
    print(f"  - {c['name']} ({c['political_lean_label']}, {c['newsguard_score']}/100)")
```

### Claim Analysis Tool

```python
# Score sources for evidence tree
evidence_urls = [
    "https://www.factcheck.org/claim-analysis",
    "https://www.brookings.edu/policy-paper",
    "https://www.wsj.com/analysis"
]

# Batch analyze
response = requests.post("http://localhost:8000/api/analyze/batch", json={
    "urls": evidence_urls,
    "options": {"include_counternarratives": False}
})

for result in response.json()["results"]:
    if result["source_found"]:
        source = result["source"]

        # Score for claim context
        score_response = requests.post("http://localhost:8000/api/sources/score", json={
            "domain": source["domain"],
            "context": {
                "claim_type": "political",
                "evidence_role": "support",
                "preferred_credibility": "high"
            }
        })

        scoring = score_response.json()
        print(f"{source['name']}: {scoring['weighted_score']}/100 ({scoring['recommendation']})")
```

---

## Configuration

Edit `.env` file to customize settings:

```bash
# Database path
DB_PATH=/path/to/sources.db

# API server
API_HOST=0.0.0.0
API_PORT=8000

# CORS (for web UI)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Defaults
DEFAULT_MIN_CREDIBILITY=60
DEFAULT_COUNTERNARRATIVE_LIMIT=10
```

---

## Development

### Run with Auto-Reload

```bash
uvicorn api.main:app --reload
```

### Run Tests (coming soon)

```bash
pytest
```

---

## Database

The API uses the existing SQLite database at `data/sources.db` with **222 sources**.

**Current Coverage**:
- 95 sources with NewsGuard ratings
- 143 sources with political lean data
- 17 fact-checkers
- International sources (Asia, Europe, Latin America, Africa)
- Specialized verticals (tech, business, science, sports)

---

## Support

- **Issues**: Report bugs or request features
- **Documentation**: Full API docs at `/docs`
- **Database**: See `README.md` for source management

---

## Roadmap

**Phase 2** (Future):
- Topic-aware counternarrative matching
- Markdown export format
- Obsidian integration
- Source tagging system (topics, evidence types)
- Authentication for admin endpoints
- Caching layer for performance

---

**Built with**: FastAPI, SQLite, Python 3.12
