import random
import time
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import httpx

class BaseScraper(ABC):
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    ]

    def __init__(self, retries: int = 3, backoff_factor: float = 0.5):
        self.user_agent = random.choice(self.USER_AGENTS)
        self.retries = retries
        self.backoff_factor = backoff_factor

    def get_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    async def fetch(self, url: str, params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        async with httpx.AsyncClient(headers=self.get_headers(), follow_redirects=True, timeout=30.0) as client:
            for i in range(self.retries):
                try:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    return response
                except (httpx.RequestError, httpx.HTTPStatusError) as e:
                    if i == self.retries - 1:
                        raise e
                    sleep_time = self.backoff_factor * (2 ** i)
                    await asyncio.sleep(sleep_time)
        raise httpx.RequestError("Maximum retries reached")

    @abstractmethod
    async def scrape(self, query: str) -> Dict[str, Any]:
        """Method to implement the scraping logic for a specific provider."""
        pass
