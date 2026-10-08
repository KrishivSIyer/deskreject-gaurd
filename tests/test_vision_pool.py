import json
from io import BytesIO
from pathlib import Path

import httpx
from PIL import Image

from deskreject.config import Endpoint
from deskreject.vision.pool import VisionJob, VisionPool


def create_test_image_bytes():
    img = Image.new("RGB", (100, 100), color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_vision_pool_cache_hit(tmp_path: Path):
    endpoints = [Endpoint(model="gemma4:12b", url="http://127.0.0.1:11434")]
    pool = VisionPool(endpoints, cache_dir=tmp_path)
    
    img_bytes = create_test_image_bytes()
    job = VisionJob(image_png=img_bytes, prompt="test", schema_dict={"type": "object"}, tag="test")
    
    # Pre-populate cache
    pool.cache.set(job.image_png, job.prompt, job.schema_dict, {"result": "cached"})
    
    result = pool.ask(job)
    assert result.ok
    assert result.cached
    assert result.data == {"result": "cached"}
    assert pool.stats["cache_hits"] == 1


def test_vision_pool_json_retry(tmp_path: Path):
    endpoints = [Endpoint(model="gemma4:12b", url="http://127.0.0.1:11434")]
    
    call_count = 0
    def handler(request: httpx.Request):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # First call returns bad JSON
            return httpx.Response(200, json={"message": {"content": "not json"}})
        else:
            return httpx.Response(200, json={"message": {"content": '{"success": true}'}})
            
    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    
    pool = VisionPool(endpoints, cache_dir=tmp_path, http_client=client)
    img_bytes = create_test_image_bytes()
    job = VisionJob(image_png=img_bytes, prompt="test", schema_dict={"type": "object"}, tag="test")
    
    result = pool.ask(job)
    assert result.ok
    assert result.data == {"success": True}
    assert call_count == 2
    assert pool.stats["calls"] == 1  # Total original jobs (not retries)


def test_vision_pool_dead_endpoint_failover(tmp_path: Path):
    ep1 = Endpoint(model="gemma4:12b", url="http://127.0.0.1:11434")
    ep2 = Endpoint(model="gemma4:e4b", url="http://192.168.43.101:11434")
    endpoints = [ep1, ep2]
    
    def handler(request: httpx.Request):
        if "127.0.0.1" in str(request.url):
            return httpx.Response(500)
        return httpx.Response(200, json={"message": {"content": '{"success": true}'}})
        
    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    
    pool = VisionPool(endpoints, cache_dir=tmp_path, http_client=client)
    
    # We will fake the pool to prefer ep1 first by setting ep1 calls to 0 and ep2 calls to 1 temporarily
    pool.workers[1].calls = 1
    
    img_bytes = create_test_image_bytes()
    job = VisionJob(image_png=img_bytes, prompt="test", schema_dict={"type": "object"}, tag="test")
    
    result = pool.ask(job)
    assert result.ok
    assert result.data == {"success": True}
    assert result.endpoint == "http://192.168.43.101:11434"
    assert pool.workers[0].failures > 0


def test_vision_pool_job_order_preservation(tmp_path: Path):
    ep1 = Endpoint(model="gemma4:12b", url="http://127.0.0.1:11434")
    endpoints = [ep1]
    
    def handler(request: httpx.Request):
        # We can extract the prompt from the request body to know which job this is
        body = json.loads(request.read())
        prompt = body["messages"][0]["content"]
        return httpx.Response(200, json={"message": {"content": f'{{"prompt": "{prompt}"}}'}})
        
    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    
    pool = VisionPool(endpoints, cache_dir=tmp_path, http_client=client)
    
    img_bytes = create_test_image_bytes()
    jobs = [
        VisionJob(image_png=img_bytes, prompt="job1", schema_dict={}, tag="1"),
        VisionJob(image_png=img_bytes, prompt="job2", schema_dict={}, tag="2"),
        VisionJob(image_png=img_bytes, prompt="job3", schema_dict={}, tag="3"),
    ]
    
    results = pool.ask_many(jobs)
    assert len(results) == 3
    assert results[0].data == {"prompt": "job1"}
    assert results[1].data == {"prompt": "job2"}
    assert results[2].data == {"prompt": "job3"}
