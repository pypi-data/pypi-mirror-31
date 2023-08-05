from typing import Optional


class CacheBackend:
    async def get(self, key: str, format: str = 'html') -> Optional[bytes]:
        raise NotImplementedError

    def set(self, key: str, payload: bytes, ttl: int = None, format: str = 'html') -> None:
        raise NotImplementedError

    async def modified_since(self, key: str, format: str = 'html') -> Optional[float]:
        raise NotImplementedError
