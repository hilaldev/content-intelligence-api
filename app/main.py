from fastapi import FastAPI, HTTPException, Depends, Header
from app.models import *
from app.services import generate_ecom_content, generate_ads_content, generate_research_brief
import os
import asyncio

app = FastAPI(
    title="Content Intelligence API",
    version="1.0.0",
    description="Professional API for eCommerce, Ads, and SEO Research."
)

# --- Security ---
API_SECRET = os.getenv("API_SECRET", "dev-secret-key")

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_SECRET:
        raise HTTPException(status_code=401, detail="Invalid API Key")

# --- Phase 1: eCommerce Endpoints ---
@app.post("/api/v1/ecommerce/generate", response_model=EcomResponse, dependencies=[Depends(verify_api_key)])
async def create_product_content(request: EcomRequest):
    try:
        return await generate_ecom_content(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Phase 2: Ads & SEO Endpoints ---
@app.post("/api/v1/ads/generate", response_model=AdResponse, dependencies=[Depends(verify_api_key)])
async def create_ad_copy(request: AdRequest):
    try:
        return await generate_ads_content(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ads/bulk", dependencies=[Depends(verify_api_key)])
async def bulk_ad_copy(request: BulkAdRequest):
    results = []
    # Process in chunks of 5 to avoid hitting OpenAI rate limits
    chunk_size = 5
    
    for i in range(0, len(request.items), chunk_size):
        chunk = request.items[i:i + chunk_size]
        # Run this chunk in parallel
        tasks = [generate_ads_content(item) for item in chunk]
        chunk_results = await asyncio.gather(*tasks, return_exceptions=True)
        results.extend(chunk_results)
        
    return {"results": results, "count": len(results)}

# --- Phase 3: Research Endpoints ---
@app.post("/api/v1/content/research", response_model=ContentBriefResponse, dependencies=[Depends(verify_api_key)])
async def create_content_brief(request: ResearchRequest):
    try:
        return await generate_research_brief(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health_check():
    return {"status": "active", "phases": ["ecommerce", "ads", "research"]}