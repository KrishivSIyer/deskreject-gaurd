import httpx
import pytest

from deskreject.netguard import BlockedHost, blocked_count, make_client


class DummyEndpoint:
    def __init__(self, url):
        self.url = url

class DummySettings:
    def __init__(self, endpoints):
        self.ollama_vision_endpoints = endpoints

def test_netguard_blocks_external():
    settings = DummySettings([DummyEndpoint("http://127.0.0.1:11434")])
    client = make_client(settings)
    
    initial_blocks = blocked_count()
    
    with pytest.raises(BlockedHost):
        # We don't actually want to hit the network, but the hook runs before the transport
        client.get("https://example.com")
        
    assert blocked_count() == initial_blocks + 1

def test_netguard_allows_internal(monkeypatch):
    settings = DummySettings([DummyEndpoint("http://127.0.0.1:11434")])
    client = make_client(settings)
    
    # Mock transport so we don't actually connect
    class MockTransport(httpx.BaseTransport):
        def handle_request(self, request):
            return httpx.Response(200, request=request)
            
    client._transport = MockTransport()
    
    response = client.get("http://127.0.0.1:11434/api/tags")
    assert response.status_code == 200
