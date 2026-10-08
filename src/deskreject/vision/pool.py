import concurrent.futures
import time
from pathlib import Path

import httpx
from pydantic import BaseModel

from deskreject.config import Endpoint
from deskreject.vision.cache import VisionCache
from deskreject.vision.client import OllamaVisionClient


class VisionJob(BaseModel):
    image_png: bytes
    prompt: str
    schema_dict: dict
    tag: str


class VisionResult(BaseModel):
    ok: bool
    data: dict | None
    endpoint: str | None
    model: str | None
    seconds: float
    cached: bool
    error: str | None


class WorkerState:
    def __init__(self, endpoint: Endpoint, client: httpx.Client | None = None) -> None:
        self.endpoint = endpoint
        self.client = OllamaVisionClient(endpoint, client=client)
        self.failures = 0
        self.is_healthy = True
        self.calls = 0
        self.total_seconds = 0.0


class VisionPool:
    """Multi-endpoint vision job distribution with retries and caching."""

    def __init__(
        self,
        endpoints: list[Endpoint],
        cache_dir: Path,
        use_cache: bool = True,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.workers = [WorkerState(ep, client=http_client) for ep in endpoints]
        self.cache = VisionCache(cache_dir)
        self.use_cache = use_cache
        self.stats = {
            "calls": 0,
            "cache_hits": 0,
            "failures": 0,
        }

    def _execute_job(self, job: VisionJob) -> VisionResult:
        if self.use_cache:
            cached_data = self.cache.get(job.image_png, job.prompt, job.schema_dict)
            if cached_data is not None:
                self.stats["cache_hits"] += 1
                return VisionResult(
                    ok=True,
                    data=cached_data,
                    endpoint=None,
                    model=None,
                    seconds=0.0,
                    cached=True,
                    error=None,
                )

        self.stats["calls"] += 1
        retries = 0
        max_retries = 2
        last_error = None
        
        while retries <= max_retries:
            # Find a healthy worker
            healthy_workers = [w for w in self.workers if w.is_healthy]
            if not healthy_workers:
                last_error = "No healthy endpoints available"
                break
                
            # Pick worker (round robin or randomly, here we just pick the one with fewest calls)
            worker = min(healthy_workers, key=lambda w: w.calls)
            
            t0 = time.time()
            try:
                data = worker.client.chat(
                    image_png=job.image_png,
                    prompt=job.prompt,
                    schema=job.schema_dict,
                )
                t1 = time.time()
                elapsed = t1 - t0
                
                worker.calls += 1
                worker.total_seconds += elapsed
                worker.failures = 0  # Reset on success
                
                if self.use_cache:
                    self.cache.set(job.image_png, job.prompt, job.schema_dict, data)
                    
                return VisionResult(
                    ok=True,
                    data=data,
                    endpoint=worker.endpoint.url,
                    model=worker.endpoint.model,
                    seconds=elapsed,
                    cached=False,
                    error=None,
                )
            except Exception as e:  # noqa: BLE001
                t1 = time.time()
                elapsed = t1 - t0
                worker.failures += 1
                worker.total_seconds += elapsed
                if worker.failures >= 2:
                    worker.is_healthy = False
                last_error = str(e)
                retries += 1

        self.stats["failures"] += 1
        return VisionResult(
            ok=False,
            data=None,
            endpoint=None,
            model=None,
            seconds=0.0,
            cached=False,
            error=last_error,
        )

    def ask(self, job: VisionJob) -> VisionResult:
        """Process a single job."""
        return self._execute_job(job)

    def ask_many(self, jobs: list[VisionJob]) -> list[VisionResult]:
        """Process multiple jobs concurrently."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, len(self.workers))) as executor:
            # We map instead of submit to preserve order
            results = list(executor.map(self._execute_job, jobs))
        return results

    def status(self) -> list[dict]:
        """Return status for all endpoints."""
        return [
            {
                "url": w.endpoint.url,
                "model": w.endpoint.model,
                "healthy": w.is_healthy,
                "calls": w.calls,
                "seconds": w.total_seconds,
            }
            for w in self.workers
        ]

    def get_vision_stats(self) -> dict:
        """Return combined stats for the report."""
        per_endpoint = {
            w.endpoint.url: {"calls": w.calls, "seconds": w.total_seconds}
            for w in self.workers
        }
        return {
            "calls": self.stats["calls"],
            "cache_hits": self.stats["cache_hits"],
            "failures": self.stats["failures"],
            "per_endpoint": per_endpoint,
        }
