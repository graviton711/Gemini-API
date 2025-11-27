from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
from key_manager import KeyManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GeminiProxy")

app = FastAPI()
key_manager = KeyManager()

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com"

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    return response

@app.get("/")
async def root():
    return {
        "message": "Gemini API Proxy is running!",
        "usage": "Use /health to check status, or configure your SDK to point here.",
        "docs": "https://github.com/graviton711/Gemini-API"
    }

@app.get("/health")
async def health_check():
    return {"status": "ok", "stats": key_manager.get_key_stats()}

@app.api_route("/v1beta/models/{model}:generateContent", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
@app.api_route("/v1beta/models/{model}:streamGenerateContent", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy(request: Request, path: str = None, model: str = None):
    if model:
        # Reconstruct path if matched via specific route
        if request.url.path.endswith(":generateContent"):
            path = f"v1beta/models/{model}:generateContent"
        elif request.url.path.endswith(":streamGenerateContent"):
            path = f"v1beta/models/{model}:streamGenerateContent"
    
    # Get an available key
    api_key = await key_manager.get_available_key()
    
    if not api_key:
        logger.error("No available API keys found (rate limits exhausted).")
        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "code": 429,
                    "message": "Resource exhausted: All API keys are currently rate limited. Please try again later.",
                    "status": "RESOURCE_EXHAUSTED"
                }
            }
        )

    # Construct the target URL
    url = f"{GEMINI_BASE_URL}/{path}"
    
    params = dict(request.query_params)
    params["key"] = api_key
    
    # Prepare headers (exclude host to avoid conflicts)
    # headers = {k: v for k, v in request.headers.items() if k.lower() != 'host'}
    # Only forward Content-Type for now to avoid issues
    headers = {}
    if "content-type" in request.headers:
        headers["Content-Type"] = request.headers["content-type"]
    
    await key_manager.record_usage(api_key)
    
    logger.info(f"Forwarding request to {url} using key ending in ...{api_key[-4:]}")

    async with httpx.AsyncClient() as client:
        try:
            content = await request.body()
            
            logger.info(f"Sending request to {url}")
            r = await client.request(
                request.method,
                url,
                headers=headers,
                params=params,
                content=content,
                timeout=60.0
            )
            logger.info(f"Received response status: {r.status_code}")
            
            # Return standard response
            # We should forward headers too? Maybe not all.
            # Let's just forward content-type.
            resp_headers = {}
            if "content-type" in r.headers:
                resp_headers["Content-Type"] = r.headers["content-type"]
                
            return Response(
                content=r.content,
                status_code=r.status_code,
                headers=resp_headers
            )
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"Error during proxy request: {e}")
            return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
