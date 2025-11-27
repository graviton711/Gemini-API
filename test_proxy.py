import asyncio
import httpx
import time

PROXY_URL = "http://localhost:8000/v1beta/models/gemini-2.5-pro:generateContent"
HEALTH_URL = "http://localhost:8000/health"

async def make_request(i):
    async with httpx.AsyncClient() as client:
        try:
            # We don't need a real payload for the proxy logic test, 
            # but to avoid 400 from Google, we might want a valid one.
            # However, we are testing the PROXY's rotation, so even a 400 from Google 
            # means the proxy worked and forwarded the request.
            # Let's use a dummy payload.
            payload = {
                "contents": [{
                    "parts": [{"text": "Hello"}]
                }]
            }
            
            start = time.time()
            response = await client.post(PROXY_URL, json=payload, timeout=10)
            end = time.time()
            
            print(f"Request {i}: Status {response.status_code}, Time: {end-start:.2f}s")
            return response.status_code
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Request {i}: Failed - {e!r}")
            return None

async def main():
    print("--- Starting Stress Test ---")
    
    # 1. Check Health
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(HEALTH_URL)
            print(f"Health Check: {resp.json()}")
        except Exception as e:
            print(f"Health Check Failed: {e}")
            return

    # 2. Make multiple concurrent requests to trigger rotation
    # We have ~12 keys. 2 req/min each = 24 req/min total capacity.
    # Let's try sending 10 requests quickly.
    
    tasks = [make_request(i) for i in range(10)]
    await asyncio.gather(*tasks)
    
    # 3. Check stats again
    async with httpx.AsyncClient() as client:
        resp = await client.get(HEALTH_URL)
        print(f"Stats after test: {resp.json()}")

if __name__ == "__main__":
    asyncio.run(main())
