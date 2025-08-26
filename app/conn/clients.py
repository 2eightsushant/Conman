import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

DEFAULT_TIMEOUT = httpx.Timeout(connect=2.0, read=20.0, write=5.0, pool=10.0)
_client: httpx.AsyncClient | None = None

def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=DEFAULT_TIMEOUT)
    return _client

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4))
async def post_json(client: httpx.AsyncClient, url: str, payload: dict) -> dict:
    resp = await client.post(url, json=payload)
    resp.raise_for_status()
    return resp.json()

async def get_json(client: httpx.AsyncClient, url: str) -> dict:
    resp = await client.get(url)
    resp.raise_for_status()
    return resp.json()