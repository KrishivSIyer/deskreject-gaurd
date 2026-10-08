import httpx
import pytest

from deskreject.config import Endpoint, Settings
from deskreject.netguard import BlockedHost, _reset_blocked_count, blocked_count, make_client


def test_netguard_blocks_unauthorized_host():
    _reset_blocked_count()
    initial_count = blocked_count()
    
    settings = Settings(
        ollama_vision_endpoints=[Endpoint(model="gemma4:12b", url="http://127.0.0.1:11434")],
        text_model="text",
        coder_model="coder",
    )
    
    transport = httpx.MockTransport(lambda request: httpx.Response(200, text="OK"))
    client = make_client(settings, transport=transport)
    
    with pytest.raises(BlockedHost):
        client.get("https://example.com/api")
        
    assert blocked_count() == initial_count + 1


def test_netguard_allows_authorized_host():
    _reset_blocked_count()
    
    settings = Settings(
        ollama_vision_endpoints=[Endpoint(model="gemma4:12b", url="http://127.0.0.1:11434")],
        text_model="text",
        coder_model="coder",
    )
    
    transport = httpx.MockTransport(lambda request: httpx.Response(200, text="OK"))
    client = make_client(settings, transport=transport)
    
    response = client.get("http://127.0.0.1:11434/api/tags")
    assert response.status_code == 200
    assert blocked_count() == 0
