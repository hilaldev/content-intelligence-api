import os
import requests
from litellm import completion
from app.models import EcomRequest, AdRequest, ResearchRequest
from app.utils import enforce_char_limit

# Configuration
OPENAI_MODEL = "gpt-3.5-turbo" # Or gpt-4-turbo for better quality
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

async def generate_ecom_content(data: EcomRequest):
    """Phase 1: Generates Product Data"""
    
    system_prompt = f"""
    You are an expert copywriter for {data.platform}. 
    Tone: {data.tone}.
    Return JSON format only.
    Structure: title, description_html (use <b> for emphasis), bullet_points (list), seo_tags (list).
    """
    
    user_prompt = f"Product: {data.product_name}. Features: {', '.join(data.features)}"
    
    response = completion(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    # Parse JSON from LLM
    import json
    content = json.loads(response.choices[0].message.content)
    return content

async def generate_ads_content(data: AdRequest):
    """Phase 2: Generates Ads with Validation"""
    
    prompt = f"""
    Write ad copy for {data.product_name}.
    Audience: {data.target_audience}.
    Keywords: {', '.join(data.keywords)}.
    
    Return JSON:
    - facebook_primary_text
    - facebook_headline
    - google_headline (strict max 30 chars, catchy)
    - google_description (strict max 90 chars)
    - meta_title (SEO optimized)
    - meta_description
    """
    
    response = completion(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    content = json.loads(response.choices[0].message.content)
    
    # PROFESSIONAL STEP: Post-processing validation
    # If the LLM failed the char limit, we force truncate it here.
    content['google_headline'] = enforce_char_limit(content['google_headline'], 30)
    content['google_description'] = enforce_char_limit(content['google_description'], 90)
    
    return content

async def generate_research_brief(data: ResearchRequest):
    """Phase 3: Fetches Real Google Data + LLM Synthesis"""
    
    if not SERPER_API_KEY:
        raise Exception("SERPER_API_KEY is not set on the server.")

    # 1. Fetch Real Data from Google
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": data.topic, "gl": data.country})
    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
    
    search_res = requests.request("POST", url, headers=headers, data=payload).json()
    
    # Extract relevant bits to save token costs
    organic = search_res.get('organic', [])[:5]
    questions = search_res.get('peopleAlsoAsk', [])
    
    context_data = f"Top Results: {[r['title'] for r in organic]}. People Ask: {[q['question'] for q in questions]}"

    # 2. Synthesize with LLM
    prompt = f"""
    Create a Content Brief for '{data.topic}'.
    Based on real search data: {context_data}
    
    Return JSON:
    - topic
    - search_volume_intent (Infer this from the questions)
    - competitor_urls (List of URLs from top results)
    - people_also_ask (List of questions)
    - content_outline (List of H2 headings for a blog post)
    """
    
    response = completion(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)

import json