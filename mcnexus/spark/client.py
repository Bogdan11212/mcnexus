import aiohttp
import re
from typing import Optional, Dict, Any
from mcnexus.spark.exceptions import SparkFetchError, SparkInvalidURLError

class SparkClient:
    """
    Handles fetching raw JSON data from spark.lucko.me.
    """
    # Pattern to extract ID from URL: https://spark.lucko.me/abc12345
    ID_PATTERN = re.compile(r'spark\.lucko\.me/([a-zA-Z0-9]+)')

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    def _extract_id(self, url: str) -> str:
        match = self.ID_PATTERN.search(url)
        if not match:
            raise SparkInvalidURLError(f"Could not extract profile ID from URL: {url}")
        return match.group(1)

    async def fetch_raw_data(self, url_or_id: str, include_full: bool = True) -> Dict[str, Any]:
        """
        Fetches raw JSON data for a profile.
        """
        profile_id = url_or_id
        if "spark.lucko.me" in url_or_id:
            profile_id = self._extract_id(url_or_id)

        api_url = f"https://spark.lucko.me/{profile_id}?raw=1"
        if include_full:
            api_url += "&full=true"

        try:
            async with self.session.get(api_url) as resp:
                if resp.status != 200:
                    raise SparkFetchError(f"Failed to fetch spark data: HTTP {resp.status}")
                return await resp.json()
        except aiohttp.ClientError as e:
            raise SparkFetchError(f"Network error while fetching spark data: {e}")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
