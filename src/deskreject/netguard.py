from urllib.parse import urlparse

import httpx


class BlockedHost(Exception):
    pass

_blocked_requests = 0

def blocked_count() -> int:
    return _blocked_requests

def make_client(settings, timeout=None, **kwargs) -> httpx.Client:
    allowed_hosts = [urlparse(ep.url).netloc for ep in settings.ollama_vision_endpoints]
    if getattr(settings, "text_model", None) and "@" in settings.text_model:
        allowed_hosts.append(urlparse(settings.text_model.split("@")[1]).netloc)
    if getattr(settings, "coder_model", None) and "@" in settings.coder_model:
        allowed_hosts.append(urlparse(settings.coder_model.split("@")[1]).netloc)


    def check_host(request: httpx.Request):
        global _blocked_requests
        req_netloc = request.url.host
        if request.url.port:
            req_netloc += f":{request.url.port}"
            
        if req_netloc not in allowed_hosts and request.url.host not in allowed_hosts:
            _blocked_requests += 1
            raise BlockedHost(f"Blocked request to {request.url}")

    event_hooks = kwargs.pop("event_hooks", {})
    if "request" in event_hooks:
        event_hooks["request"].insert(0, check_host)
    else:
        event_hooks["request"] = [check_host]

    client = httpx.Client(timeout=timeout, event_hooks=event_hooks, **kwargs)
    return client
