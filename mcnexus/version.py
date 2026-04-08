import aiohttp
import logging
import sys
from typing import Optional
from mcnexus import __version__ as local_version

# We use simple string splitting for version comparison to avoid extra dependencies
# but if 'packaging' is available in the environment, we could use it.

logger = logging.getLogger(__name__)

class VersionManager:
    """
    Handles automatic version checking against the GitHub main branch.
    """
    GITHUB_RAW_URL = "https://raw.githubusercontent.com/Bogdan11212/mcnexus/main/pyproject.toml"

    @staticmethod
    def _is_newer(remote: str, local: str) -> bool:
        """Simple semver comparison."""
        try:
            r_parts = [int(x) for x in remote.split('.')]
            l_parts = [int(x) for x in local.split('.')]
            return r_parts > l_parts
        except Exception:
            return False

    @classmethod
    async def check_for_updates(cls):
        """
        Fetches the latest version from GitHub and notifies the user if an update is available.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(cls.GITHUB_RAW_URL, timeout=3.0) as resp:
                    if resp.status != 200:
                        return
                    
                    content = await resp.text()
                    # Basic parsing of version = "X.Y.Z" in pyproject.toml
                    import re
                    match = re.search(r'version\s*=\s*"([^"]+)"', content)
                    if not match:
                        return
                    
                    remote_version = match.group(1)
                    
                    if cls._is_newer(remote_version, local_version):
                        cls._print_notification(remote_version)
        except Exception:
            # Silently fail to not interrupt user script
            pass

    @staticmethod
    def _print_notification(new_version: str):
        """Prints a professional update notification to stderr."""
        msg = (
            f"\n\033[92m[mcnexus] A new version is available: \033[1m{new_version}\033[0m\033[92m "
            f"(Current: {local_version})\033[0m\n"
            f"\033[94m[mcnexus] New modules and features have been added! \033[0m\n"
            f"\033[94m[mcnexus] Update now using: \033[1mpip install --upgrade mcnexus\033[0m\n"
        )
        print(msg, file=sys.stderr)
