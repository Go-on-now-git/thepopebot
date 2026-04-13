#!/usr/bin/env python3
"""
Tax Deed Surplus Funds Scraper
Asynchronous, resource-optimized scraper for Termux environments.
Extracts surplus funds exceeding $10,000 from municipal public records.
"""

import asyncio
import json
import gzip
import random
import re
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any, Set
from difflib import SequenceMatcher
from urllib.parse import urljoin, urlparse
import logging

try:
    import aiohttp
    from aiohttp import ClientTimeout, TCPConnector
except ImportError:
    raise ImportError("aiohttp required: pip install aiohttp")

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise ImportError("beautifulsoup4 required: pip install beautifulsoup4")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
]

OWNER_COLUMN_VARIANTS = [
    "owner", "property owner", "former owner", "defendant", "taxpayer",
    "name", "party", "record owner", "titleholder", "claimant",
    "owner name", "defendant name", "property holder", "grantee"
]

SURPLUS_COLUMN_VARIANTS = [
    "surplus", "excess", "excess funds", "surplus funds", "overage",
    "surplus amount", "excess amount", "remaining funds", "balance",
    "overbid", "excess proceeds", "surplus proceeds", "amount due",
    "funds available", "unclaimed funds", "available surplus"
]

AMOUNT_THRESHOLD = 10000.0
JITTER_MIN = 0.8
JITTER_MAX = 3.4
MAX_RETRIES = 5
BASE_BACKOFF = 1.5


@dataclass
class SurplusRecord:
    """Validated surplus fund record with strict typing."""
    county: str
    municipality: str
    owner_name: str
    surplus_amount: float
    parcel_id: Optional[str] = None
    property_address: Optional[str] = None
    sale_date: Optional[str] = None
    case_number: Optional[str] = None
    source_url: str = ""
    extracted_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def __post_init__(self):
        self.owner_name = self._sanitize_text(self.owner_name)
        self.county = self._sanitize_text(self.county)
        self.municipality = self._sanitize_text(self.municipality)
        if self.property_address:
            self.property_address = self._sanitize_text(self.property_address)
        if self.parcel_id:
            self.parcel_id = self._sanitize_text(self.parcel_id)
    
    @staticmethod
    def _sanitize_text(text: str) -> str:
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'[^\w\s\-\.,#&\'/]', '', text)
        return text[:500]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ScraperConfig:
    """Configuration for scraper behavior."""
    max_concurrent: int = 3
    timeout_seconds: int = 30
    min_surplus: float = AMOUNT_THRESHOLD
    max_retries: int = MAX_RETRIES
    respect_robots: bool = True
    compress_output: bool = True


class CurrencyParser:
    """Robust currency string parser with multiple format support."""
    
    CURRENCY_PATTERNS = [
        re.compile(r'\$?\s*([\d,]+\.?\d*)', re.IGNORECASE),
        re.compile(r'([\d,]+\.?\d*)\s*(?:USD|dollars?)?', re.IGNORECASE),
        re.compile(r'(?:USD|US\$)\s*([\d,]+\.?\d*)', re.IGNORECASE),
    ]
    
    @classmethod
    def parse(cls, value: str) -> Optional[float]:
        if not value or not isinstance(value, str):
            return None
        
        cleaned = value.strip()
        cleaned = re.sub(r'[^\d.,\-$]', '', cleaned)
        
        for pattern in cls.CURRENCY_PATTERNS:
            match = pattern.search(value)
            if match:
                try:
                    amount_str = match.group(1)
                    amount_str = amount_str.replace(',', '')
                    amount = float(amount_str)
                    return round(amount, 2)
                except (ValueError, IndexError):
                    continue
        
        try:
            cleaned = re.sub(r'[,$]', '', cleaned)
            return round(float(cleaned), 2)
        except ValueError:
            return None


class FuzzyColumnMatcher:
    """Fuzzy string matching for column header identification."""
    
    def __init__(self, threshold: float = 0.65):
        self.threshold = threshold
    
    def match(self, header: str, variants: List[str]) -> bool:
        if not header:
            return False
        
        normalized = header.lower().strip()
        normalized = re.sub(r'[^\w\s]', '', normalized)
        
        if normalized in variants:
            return True
        
        for variant in variants:
            ratio = SequenceMatcher(None, normalized, variant).ratio()
            if ratio >= self.threshold:
                return True
            
            if variant in normalized or normalized in variant:
                return True
        
        return False
    
    def find_column_index(
        self, 
        headers: List[str], 
        variants: List[str]
    ) -> Optional[int]:
        for idx, header in enumerate(headers):
            if self.match(header, variants):
                return idx
        return None


class AdaptiveParser:
    """BeautifulSoup parser with regex fallback heuristics."""
    
    def __init__(self):
        self.column_matcher = FuzzyColumnMatcher()
        self.currency_parser = CurrencyParser()
    
    def parse_html(self, html: str, source_url: str, county: str, municipality: str) -> List[SurplusRecord]:
        records = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
        except Exception as e:
            logger.warning(f"BeautifulSoup parse failed: {e}")
            return self._regex_fallback(html, source_url, county, municipality)
        
        tables = soup.find_all('table')
        for table in tables:
            table_records = self._parse_table(table, source_url, county, municipality)
            records.extend(table_records)
        
        if not records:
            div_records = self._parse_div_structures(soup, source_url, county, municipality)
            records.extend(div_records)
        
        if not records:
            records = self._regex_fallback(html, source_url, county, municipality)
        
        return records
    
    def _parse_table(
        self, 
        table, 
        source_url: str, 
        county: str, 
        municipality: str
    ) -> List[SurplusRecord]:
        records = []
        
        headers = []
        header_row = table.find('tr')
        if header_row:
            header_cells = header_row.find_all(['th', 'td'])
            headers = [cell.get_text(strip=True) for cell in header_cells]
        
        owner_idx = self.column_matcher.find_column_index(headers, OWNER_COLUMN_VARIANTS)
        surplus_idx = self.column_matcher.find_column_index(headers, SURPLUS_COLUMN_VARIANTS)
        
        if owner_idx is None or surplus_idx is None:
            return records
        
        parcel_idx = self._find_parcel_column(headers)
        address_idx = self._find_address_column(headers)
        date_idx = self._find_date_column(headers)
        case_idx = self._find_case_column(headers)
        
        rows = table.find_all('tr')[1:]
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) <= max(owner_idx, surplus_idx):
                continue
            
            owner = cells[owner_idx].get_text(strip=True) if owner_idx < len(cells) else ""
            surplus_text = cells[surplus_idx].get_text(strip=True) if surplus_idx < len(cells) else ""
            
            surplus_amount = self.currency_parser.parse(surplus_text)
            if surplus_amount is None or surplus_amount < AMOUNT_THRESHOLD:
                continue
            
            if not owner or len(owner) < 2:
                continue
            
            record = SurplusRecord(
                county=county,
                municipality=municipality,
                owner_name=owner,
                surplus_amount=surplus_amount,
                parcel_id=self._safe_get_cell(cells, parcel_idx),
                property_address=self._safe_get_cell(cells, address_idx),
                sale_date=self._safe_get_cell(cells, date_idx),
                case_number=self._safe_get_cell(cells, case_idx),
                source_url=source_url
            )
            records.append(record)
        
        return records
    
    def _parse_div_structures(
        self, 
        soup, 
        source_url: str, 
        county: str, 
        municipality: str
    ) -> List[SurplusRecord]:
        records = []
        
        record_divs = soup.find_all('div', class_=re.compile(r'record|row|item|entry', re.I))
        
        for div in record_divs:
            text = div.get_text()
            
            owner = self._extract_labeled_value(text, OWNER_COLUMN_VARIANTS)
            surplus_text = self._extract_labeled_value(text, SURPLUS_COLUMN_VARIANTS)
            
            if not owner or not surplus_text:
                continue
            
            surplus_amount = self.currency_parser.parse(surplus_text)
            if surplus_amount is None or surplus_amount < AMOUNT_THRESHOLD:
                continue
            
            record = SurplusRecord(
                county=county,
                municipality=municipality,
                owner_name=owner,
                surplus_amount=surplus_amount,
                source_url=source_url
            )
            records.append(record)
        
        return records
    
    def _regex_fallback(
        self, 
        html: str, 
        source_url: str, 
        county: str, 
        municipality: str
    ) -> List[SurplusRecord]:
        records = []
        
        patterns = [
            re.compile(
                r'(?:owner|defendant|name)[:\s]*([A-Z][A-Za-z\s\-\.]+?)[\s,]+.*?'
                r'(?:surplus|excess|amount)[:\s]*\$?([\d,]+\.?\d*)',
                re.IGNORECASE | re.DOTALL
            ),
            re.compile(
                r'\$?([\d,]+\.?\d*)\s*(?:surplus|excess).*?'
                r'(?:owner|defendant|name)[:\s]*([A-Z][A-Za-z\s\-\.]+)',
                re.IGNORECASE | re.DOTALL
            ),
        ]
        
        for pattern in patterns:
            matches = pattern.findall(html)
            for match in matches:
                if len(match) >= 2:
                    if match[0][0].isdigit():
                        surplus_text, owner = match[0], match[1]
                    else:
                        owner, surplus_text = match[0], match[1]
                    
                    surplus_amount = self.currency_parser.parse(surplus_text)
                    if surplus_amount is None or surplus_amount < AMOUNT_THRESHOLD:
                        continue
                    
                    if not owner or len(owner.strip()) < 2:
                        continue
                    
                    record = SurplusRecord(
                        county=county,
                        municipality=municipality,
                        owner_name=owner.strip(),
                        surplus_amount=surplus_amount,
                        source_url=source_url
                    )
                    records.append(record)
        
        return records
    
    def _extract_labeled_value(self, text: str, labels: List[str]) -> Optional[str]:
        for label in labels:
            pattern = re.compile(
                rf'{re.escape(label)}[:\s]+([^\n\r<>]+)',
                re.IGNORECASE
            )
            match = pattern.search(text)
            if match:
                return match.group(1).strip()
        return None
    
    def _find_parcel_column(self, headers: List[str]) -> Optional[int]:
        variants = ["parcel", "parcel id", "parcel number", "pin", "folio", "apn", "tax id"]
        return self.column_matcher.find_column_index(headers, variants)
    
    def _find_address_column(self, headers: List[str]) -> Optional[int]:
        variants = ["address", "property address", "location", "property location", "situs"]
        return self.column_matcher.find_column_index(headers, variants)
    
    def _find_date_column(self, headers: List[str]) -> Optional[int]:
        variants = ["date", "sale date", "auction date", "sold", "sold date"]
        return self.column_matcher.find_column_index(headers, variants)
    
    def _find_case_column(self, headers: List[str]) -> Optional[int]:
        variants = ["case", "case number", "case #", "case no", "docket", "file number"]
        return self.column_matcher.find_column_index(headers, variants)
    
    @staticmethod
    def _safe_get_cell(cells: list, idx: Optional[int]) -> Optional[str]:
        if idx is not None and idx < len(cells):
            text = cells[idx].get_text(strip=True)
            return text if text else None
        return None


class StealthRequestHandler:
    """Handles HTTP requests with stealth features and retry logic."""
    
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self._request_times: Dict[str, float] = {}
    
    def _get_random_ua(self) -> str:
        return random.choice(USER_AGENTS)
    
    def _get_jitter(self) -> float:
        return random.uniform(JITTER_MIN, JITTER_MAX)
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": self._get_random_ua(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
    
    async def _apply_rate_limit(self, domain: str):
        last_request = self._request_times.get(domain, 0)
        elapsed = time.time() - last_request
        jitter = self._get_jitter()
        
        if elapsed < jitter:
            await asyncio.sleep(jitter - elapsed)
        
        self._request_times[domain] = time.time()
    
    def _parse_retry_after(self, response: aiohttp.ClientResponse) -> Optional[float]:
        retry_after = response.headers.get('Retry-After')
        if not retry_after:
            return None
        
        try:
            return float(retry_after)
        except ValueError:
            try:
                from email.utils import parsedate_to_datetime
                retry_date = parsedate_to_datetime(retry_after)
                return max(0, (retry_date - datetime.now(retry_date.tzinfo)).total_seconds())
            except Exception:
                return None
    
    async def fetch(self, url: str) -> Optional[str]:
        domain = urlparse(url).netloc
        
        for attempt in range(self.config.max_retries):
            try:
                await self._apply_rate_limit(domain)
                
                timeout = ClientTimeout(total=self.config.timeout_seconds)
                headers = self._get_headers()
                
                async with self.session.get(url, headers=headers, timeout=timeout, ssl=False) as response:
                    
                    if response.status == 200:
                        return await response.text()
                    
                    if response.status == 429:
                        retry_after = self._parse_retry_after(response)
                        wait_time = retry_after or (BASE_BACKOFF ** (attempt + 1))
                        wait_time += self._get_jitter()
                        logger.warning(f"Rate limited on {domain}, waiting {wait_time:.1f}s")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    if response.status in (500, 502, 503, 504):
                        wait_time = (BASE_BACKOFF ** (attempt + 1)) + self._get_jitter()
                        logger.warning(f"Server error {response.status} on {url}, retry in {wait_time:.1f}s")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    if response.status in (403, 404):
                        logger.info(f"HTTP {response.status} for {url}, skipping")
                        return None
                    
                    logger.warning(f"Unexpected status {response.status} for {url}")
                    return None
                    
            except asyncio.TimeoutError:
                wait_time = (BASE_BACKOFF ** (attempt + 1)) + self._get_jitter()
                logger.warning(f"Timeout on {url}, retry {attempt + 1}/{self.config.max_retries}")
                await asyncio.sleep(wait_time)
                
            except aiohttp.ClientError as e:
                wait_time = (BASE_BACKOFF ** (attempt + 1)) + self._get_jitter()
                logger.warning(f"Client error on {url}: {e}, retry in {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                logger.error(f"Unexpected error fetching {url}: {e}")
                return None
        
        logger.error(f"Max retries exceeded for {url}")
        return None
    
    async def __aenter__(self):
        connector = TCPConnector(
            limit=self.config.max_concurrent,
            limit_per_host=2,
            enable_cleanup_closed=True,
            force_close=True
        )
        self.session = aiohttp.ClientSession(connector=connector)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()


class SurplusFundsScraper:
    """Main scraper orchestrator."""
    
    def __init__(self, config: Optional[ScraperConfig] = None):
        self.config = config or ScraperConfig()
        self.parser = AdaptiveParser()
        self.records: List[SurplusRecord] = []
        self._seen_records: Set[str] = set()
    
    def _record_hash(self, record: SurplusRecord) -> str:
        return f"{record.county}:{record.owner_name}:{record.surplus_amount}"
    
    def _deduplicate(self, records: List[SurplusRecord]) -> List[SurplusRecord]:
        unique = []
        for record in records:
            record_hash = self._record_hash(record)
            if record_hash not in self._seen_records:
                self._seen_records.add(record_hash)
                unique.append(record)
        return unique
    
    async def scrape_source(
        self,
        handler: StealthRequestHandler,
        url: str,
        county: str,
        municipality: str
    ) -> List[SurplusRecord]:
        logger.info(f"Scraping: {url}")
        
        html = await handler.fetch(url)
        if not html:
            return []
        
        records = self.parser.parse_html(html, url, county, municipality)
        records = self._deduplicate(records)
        
        logger.info(f"Found {len(records)} records from {municipality}, {county}")
        return records
    
    async def scrape_all(
        self,
        sources: List[Dict[str, str]]
    ) -> List[SurplusRecord]:
        """
        Scrape all sources concurrently with semaphore limiting.
        
        Args:
            sources: List of dicts with keys: url, county, municipality
        """
        semaphore = asyncio.Semaphore(self.config.max_concurrent)
        
        async def bounded_scrape(handler: StealthRequestHandler, source: Dict[str, str]):
            async with semaphore:
                return await self.scrape_source(
                    handler,
                    source['url'],
                    source['county'],
                    source['municipality']
                )
        
        async with StealthRequestHandler(self.config) as handler:
            tasks = [
                bounded_scrape(handler, source)
                for source in sources
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_records = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Scrape task failed: {result}")
            elif result:
                all_records.extend(result)
        
        self.records = all_records
        return all_records
    
    def to_nested_json(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """Organize records by county/municipality hierarchy."""
        nested: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        
        for record in self.records:
            county = record.county or "Unknown County"
            municipality = record.municipality or "Unknown Municipality"
            
            if county not in nested:
                nested[county] = {}
            
            if municipality not in nested[county]:
                nested[county][municipality] = []
            
            nested[county][municipality].append(record.to_dict())
        
        return nested
    
    def export_json(self, filepath: str, compress: bool = True) -> str:
        """Export records to JSON file."""
        data = {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "total_records": len(self.records),
                "threshold_amount": AMOUNT_THRESHOLD,
                "counties_count": len(set(r.county for r in self.records)),
            },
            "records_by_location": self.to_nested_json()
        }
        
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        if compress:
            filepath = filepath if filepath.endswith('.gz') else f"{filepath}.gz"
            with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                f.write(json_str)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_str)
        
        logger.info(f"Exported {len(self.records)} records to {filepath}")
        return filepath


SAMPLE_SOURCES = [
    {
        "url": "https://example-county.gov/surplus-funds",
        "county": "Example County",
        "municipality": "County Clerk"
    },
]


async def main():
    """Main entry point."""
    config = ScraperConfig(
        max_concurrent=3,
        timeout_seconds=30,
        min_surplus=10000.0,
        max_retries=5,
        compress_output=True
    )
    
    scraper = SurplusFundsScraper(config)
    
    records = await scraper.scrape_all(SAMPLE_SOURCES)
    
    if records:
        output_path = scraper.export_json("surplus_funds_data.json")
        print(f"\nExported {len(records)} records to {output_path}")
        
        print("\nSummary by County:")
        nested = scraper.to_nested_json()
        for county, municipalities in nested.items():
            total = sum(len(m) for m in municipalities.values())
            print(f"  {county}: {total} records")
    else:
        print("No records found matching criteria.")
    
    return records


if __name__ == "__main__":
    asyncio.run(main())
