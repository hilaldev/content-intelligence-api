from pydantic import BaseModel, Field
from typing import List, Optional

# --- Phase 1: eCommerce ---
class EcomRequest(BaseModel):
    product_name: str
    features: List[str]
    platform: str = Field("Shopify", description="Shopify, Amazon, or Etsy")
    tone: str = "Persuasive"

class EcomResponse(BaseModel):
    title: str
    description_html: str
    bullet_points: List[str]
    seo_tags: List[str]

# --- Phase 2: Ads & SEO ---
class AdRequest(BaseModel):
    product_name: str
    target_audience: str
    keywords: List[str]

class AdResponse(BaseModel):
    facebook_primary_text: str
    facebook_headline: str
    google_headline: str = Field(..., description="Max 30 chars")
    google_description: str = Field(..., description="Max 90 chars")
    meta_title: str
    meta_description: str

class BulkAdRequest(BaseModel):
    items: List[AdRequest]

# --- Phase 3: Research & Content ---
class ResearchRequest(BaseModel):
    topic: str
    country: str = "us"

class ContentBriefResponse(BaseModel):
    topic: str
    search_volume_intent: str
    competitor_urls: List[str]
    people_also_ask: List[str]
    content_outline: List[str]