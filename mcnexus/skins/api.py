import aiohttp
from typing import Optional, Literal
from mcnexus.skins.exceptions import SkinFetchError, InvalidSizeError

class SkinsAPI:
    """
    Asynchronous engine for fetching and rendering Minecraft player skins.
    Supports Crafatar and Visage providers.
    """
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        self._session = session
        self._owns_session = session is None

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
            self._owns_session = True
        return self._session

    def get_avatar_url(self, uuid: str, size: int = 64, overlay: bool = True) -> str:
        """Returns URL for a 2D avatar (face)."""
        if not (8 <= size <= 512): raise InvalidSizeError("Size must be between 8 and 512")
        return f"https://crafatar.com/avatars/{uuid}?size={size}{'&overlay' if overlay else ''}"

    def get_head_url(self, uuid: str, size: int = 64, overlay: bool = True) -> str:
        """Returns URL for a 3D isometric head."""
        return f"https://crafatar.com/renders/head/{uuid}?size={size}{'&overlay' if overlay else ''}"

    def get_body_url(self, uuid: str, size: int = 180, overlay: bool = True) -> str:
        """Returns URL for a full 3D body render."""
        return f"https://crafatar.com/renders/body/{uuid}?size={size}{'&overlay' if overlay else ''}"

    def get_skin_file_url(self, uuid: str) -> str:
        """Returns URL for the raw .png skin texture."""
        return f"https://crafatar.com/skins/{uuid}"

    def get_visage_render_url(
        self, 
        uuid: str, 
        type: Literal["face", "bust", "full", "skin"] = "full", 
        size: int = 256
    ) -> str:
        """Returns URL from Visage (alternative provider with high-quality lighting)."""
        return f"https://visage.surgeplay.com/{type}/{size}/{uuid}"

    async def download_image(self, url: str, save_path: str) -> None:
        """Downloads an image from URL and saves it to a file."""
        try:
            async with self.session.get(url) as resp:
                if resp.status != 200:
                    raise SkinFetchError(f"Failed to download image: HTTP {resp.status}")
                
                content = await resp.read()
                with open(save_path, "wb") as f:
                    f.write(content)
        except Exception as e:
            if isinstance(e, SkinFetchError): raise
            raise SkinFetchError(f"Network error during skin download: {e}")

    async def close(self):
        if self._owns_session and self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
