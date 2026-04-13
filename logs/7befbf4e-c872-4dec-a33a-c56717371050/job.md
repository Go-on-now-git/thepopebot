Develop a highly optimized, asynchronous Python scraping architecture for deployment within a resource-constrained Termux environment. The system must autonomously identify and extract tax deed surplus funds exceeding $10,000 threshold from fragmented municipal public record databases.

Technical Requirements:
1. Asynchronous Engine: Replace synchronous requests with aiohttp for non-blocking I/O. Use asyncio.gather with strict semaphore concurrency limits to prevent Termux resource exhaustion and respect target server loads.

2. Adaptive Parsing Heuristics: Implement BeautifulSoup augmented with fallback regex patterns to navigate dynamic DOM structures. Parser must intelligently identify varying target columns ('Owner', 'Defendant', 'Surplus', 'Excess Funds') using fuzzy string matching for municipal inconsistencies.

3. Stealth & Resilience: Implement robust Retry-After header parser, coupled with exponential backoff algorithms and randomized request jitter (0.8s - 3.4s) to mimic human interaction. Integrate User-Agent rotation using pre-defined array of modern mobile and desktop browser signatures to evade WAF fingerprinting.

4. Data Sanitization & Structuring: Use strict Python dataclasses (or pydantic if feasible) to validate and sanitize extracted nodes. Currency strings must be stripped of typographical symbols ($, commas) and cast to precise floating-point integers.

5. JSON Payload: Output final dataset as compressed, nested JSON string categorized by county/municipality framework.

Output Requirements: Provide exclusively the raw, production-ready Python script without markdown formatting, introductory text, or explanatory commentary.