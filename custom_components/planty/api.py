"""HTTP client for the read-only Planty API."""

from __future__ import annotations

import asyncio
from urllib.parse import urlsplit

import aiohttp

from .const import (
    API_PROFILE_PATH,
    API_SNAPSHOT_PATH,
    REQUIRED_SNAPSHOT_KEYS,
    REQUEST_TIMEOUT_SECONDS,
)


class PlantyApiError(Exception):
    """Base exception for Planty API failures."""


class PlantyAuthenticationError(PlantyApiError):
    """The configured token is invalid or revoked."""


class PlantyConnectionError(PlantyApiError):
    """The Planty server could not be reached."""


class PlantyInvalidResponseError(PlantyApiError):
    """The Planty API returned an unexpected response."""


def normalize_base_url(value: str) -> str:
    """Validate and normalize a Planty origin URL."""
    if not isinstance(value, str):
        raise ValueError("URL muss Text sein")
    parsed = urlsplit(value.strip())
    try:
        port = parsed.port
    except ValueError as error:
        raise ValueError("Ungültiger Port") from error
    if (parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname
            or parsed.username is not None or parsed.password is not None
            or parsed.path not in {"", "/"} or parsed.query or parsed.fragment):
        raise ValueError("Bitte die Planty-Serveradresse ohne Pfad angeben")
    host = parsed.hostname.lower()
    if ":" in host:
        host = f"[{host}]"
    if port is not None:
        host = f"{host}:{port}"
    return f"{parsed.scheme.lower()}://{host}"


class PlantyApi:
    """Call Planty's explicitly read-only integration endpoints."""

    def __init__(self, session: aiohttp.ClientSession, base_url: str, token: str) -> None:
        self._session = session
        self._base_url = normalize_base_url(base_url)
        self._headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    async def async_get_profile(self) -> dict[str, str]:
        """Validate credentials and return the connected account."""
        response = await self._async_get(API_PROFILE_PATH)
        username = response.get("username") if isinstance(response, dict) else None
        if not isinstance(username, str) or not username:
            raise PlantyInvalidResponseError("Planty returned no account name")
        return {"username": username}

    async def async_get_snapshot(self) -> dict[str, list[dict]]:
        """Return the gardens and items authorized for the token owner."""
        response = await self._async_get(API_SNAPSHOT_PATH)
        if not isinstance(response, dict) or any(
            not isinstance(response.get(key), list) for key in REQUIRED_SNAPSHOT_KEYS
        ):
            raise PlantyInvalidResponseError("Planty returned an invalid garden snapshot")
        return response

    async def _async_get(self, path: str) -> dict | list:
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS)
        try:
            async with self._session.get(
                f"{self._base_url}{path}", headers=self._headers, timeout=timeout
            ) as response:
                if response.status == 401:
                    raise PlantyAuthenticationError("Planty token is invalid or revoked")
                if response.status == 429:
                    raise PlantyConnectionError("Planty API rate limit reached")
                if response.status >= 400:
                    raise PlantyInvalidResponseError(f"Planty API returned HTTP {response.status}")
                try:
                    return await response.json()
                except (aiohttp.ContentTypeError, ValueError) as error:
                    raise PlantyInvalidResponseError("Planty returned invalid JSON") from error
        except (aiohttp.ClientError, asyncio.TimeoutError) as error:
            raise PlantyConnectionError("Unable to reach Planty") from error
