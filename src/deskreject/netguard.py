from urllib.parse import urlparse

import httpx

from deskreject.config import Settings

_blocked_count = 0


class BlockedHost(Exception):
    """Raised when an HTTP request attempts to reach a non-allowlisted host."""


def blocked_count() -> int:
    """Return the total number of blocked HTTP requests."""
    return _blocked_count


def _reset_blocked_count() -> None:
    """Reset the blocked count (useful for testing)."""
    global _blocked_count
    _blocked_count = 0


def make_client(settings: Settings, **kwargs) -> httpx.Client:
    """Create an httpx.Client that only allows requests to configured Ollama endpoints."""
    
    allowed_hosts = set()
    for ep in settings.ollama_vision_endpoints:
        parsed = urlparse(ep.url)
        if parsed.hostname:
            allowed_hosts.add(parsed.hostname)

    def hook(request: httpx.Request) -> None:
        global _blocked_count
        if request.url.host not in allowed_hosts:
            _blocked_count += 1
            raise BlockedHost(f"Host {request.url.host} is not in the allowlist.")

    if "event_hooks" not in kwargs:
        kwargs["event_hooks"] = {"request": [hook]}
    else:
        if "request" not in kwargs["event_hooks"]:
            kwargs["event_hooks"]["request"] = [hook]
        else:
            kwargs["event_hooks"]["request"].append(hook)

    return httpx.Client(**kwargs)
