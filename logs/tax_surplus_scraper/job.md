# Tax Deed Surplus Funds Scraper

## Deliverable

Production-ready asynchronous Python scraper optimized for Termux deployment.

**File:** `surplus_scraper.py`

## Technical Implementation

### 1. Asynchronous Engine
- `aiohttp` with `TCPConnector` for non-blocking I/O
- `asyncio.Semaphore` limits concurrency (default: 3 concurrent requests)
- Per-host connection limiting (2) to prevent resource exhaustion

### 2. Adaptive Parsing Heuristics
- BeautifulSoup primary parser with three fallback strategies:
  - Table parsing with fuzzy column matching
  - Div/record structure parsing
  - Regex fallback for unstructured HTML
- `FuzzyColumnMatcher` uses `SequenceMatcher` (threshold: 0.65) to handle municipal naming inconsistencies

### 3. Stealth & Resilience
- Exponential backoff with base 1.5 multiplier
- Randomized jitter: 0.8s - 3.4s between requests
- `Retry-After` header parsing (numeric and HTTP-date formats)
- 8-signature User-Agent rotation (mobile + desktop)
- Per-domain rate limiting tracker

### 4. Data Sanitization
- `@dataclass` with `__post_init__` validation
- `CurrencyParser` strips `$`, commas, handles multiple formats
- Returns `float` rounded to 2 decimal places
- Text sanitization removes dangerous characters, limits length

### 5. JSON Output
- Nested structure: `county → municipality → records[]`
- Gzip compression enabled by default
- Metadata includes generation timestamp, record count, threshold

## Usage

```python
import asyncio

sources = [
    {"url": "https://county.gov/surplus", "county": "Miami-Dade", "municipality": "Clerk of Courts"}
]

config = ScraperConfig(max_concurrent=3, min_surplus=10000.0)
scraper = SurplusFundsScraper(config)
records = asyncio.run(scraper.scrape_all(sources))
scraper.export_json("output.json")
```

## Dependencies

```
aiohttp>=3.9.0
beautifulsoup4>=4.12.0
```
