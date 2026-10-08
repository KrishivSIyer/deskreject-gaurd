from urllib.parse import urlparse

import httpx


class BlockedHost(Exception):
    pass

_blocked_requests = 0

def blocked_count() -> int:
    return _blocked_requests

def make_client(settings) -> httpx.Client:
    allowed_hosts = [urlparse(ep.url).netloc for ep in settings.ollama_vision_endpoints]

    def check_host(request: httpx.Request):
        global _blocked_requests
        req_netloc = request.url.host
        if request.url.port:
            req_netloc += f":{request.url.port}"
            
        if req_netloc not in allowed_hosts and request.url.host not in allowed_hosts:
            _blocked_requests += 1
            raise BlockedHost(f"Blocked request to {request.url}")

    client = httpx.Client(event_hooks={"request": [check_host]})
    return client
