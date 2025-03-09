import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
import json
from typing import Optional, List, Dict, Any, Union
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load ACCESS_TOKEN from environment variable
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
if not ACCESS_TOKEN:
    raise ValueError("ACCESS_TOKEN environment variable is not set")

# Fields available for all ad types
COMMON_FIELDS = [
    "id", "ad_creation_time", "ad_creative_bodies", "ad_creative_link_captions",
    "ad_creative_link_descriptions", "ad_creative_link_titles", "ad_delivery_start_time",
    "ad_snapshot_url", "bylines", "languages", "page_id", "page_name", "publisher_platforms",
    "target_ages", "target_gender", "target_locations"
]

# Fields available only for political ads
POLITICAL_FIELDS = [
    "spend", "impressions", "currency", "estimated_audience_size", 
    "demographic_distribution", "delivery_by_region", "br_total_reach"
]

# Fields available for EU-targeted political ads
EU_POLITICAL_FIELDS = [
    "eu_total_reach", "age_country_gender_reach_breakdown", "beneficiary_payers"
]

# Fields available for non-active ads
INACTIVE_AD_FIELDS = [
    "ad_delivery_stop_time"
]

# Complete set of fields for reference
DEFAULT_FIELDS = COMMON_FIELDS + POLITICAL_FIELDS + EU_POLITICAL_FIELDS + INACTIVE_AD_FIELDS

VALID_AD_TYPES = ["ALL", "EMPLOYMENT_ADS", "FINANCIAL_PRODUCTS_AND_SERVICES_ADS",
                "HOUSING_ADS", "POLITICAL_AND_ISSUE_ADS"]

VALID_MEDIA_TYPES = ["ALL", "IMAGE", "MEME", "VIDEO", "NONE"]

VALID_AD_ACTIVE_STATUS = ["ACTIVE", "ALL", "INACTIVE"]

def fetch_ads(
    ad_reached_countries: List[str],
    access_token: str = ACCESS_TOKEN,
    search_terms: Optional[str] = None,
    ad_active_status: Optional[str] = None,
    ad_delivery_date_min: Optional[str] = None,
    ad_delivery_date_max: Optional[str] = None,
    ad_type: Optional[str] = None,
    bylines: Optional[List[str]] = None,
    delivery_by_region: Optional[List[str]] = None,
    estimated_audience_size_min: Optional[int] = None,
    estimated_audience_size_max: Optional[int] = None,
    languages: Optional[List[str]] = None,
    media_type: Optional[str] = None,
    publisher_platforms: Optional[List[str]] = None,
    search_page_ids: Optional[List[int]] = None,
    search_type: Optional[str] = None,
    unmask_removed_content: Optional[bool] = None,
    fields: Optional[List[str]] = None,
    max_results: Optional[int] = None,
    max_pages: Optional[int] = None,
    limit_per_request: int = 100,
    api_version: str = "v12.0",
    timeout: int = 30,
    max_retries: int = 5,
    optimize_fields: bool = True,
    verbose: bool = False  # NEW parameter to control detailed logging
) -> List[Dict[str, Any]]:
    """
    Fetches ads from Meta's Ad Library API with comprehensive parameter handling and pagination.
    
    ALL THE AVAILABLE SEARCH PARAMETERS ARE EXPOSED as function parameters.
    This includes:
      - ad_active_status(enum): ACTIVE, ALL, INACTIVE
      - ad_delivery_date_min and ad_delivery_date_max (string, YYYY-mm-dd)
      - ad_reached_countries (list of country codes; required)
      - ad_type(enum): ALL, EMPLOYMENT_ADS, FINANCIAL_PRODUCTS_AND_SERVICES_ADS, HOUSING_ADS, POLITICAL_AND_ISSUE_ADS
      - bylines (list of strings)
      - delivery_by_region (list of regions)
      - estimated_audience_size_min and estimated_audience_size_max (integers from allowed range boundaries)
      - languages (list of ISO language codes)
      - media_type(enum): ALL, IMAGE, MEME, VIDEO, NONE
      - publisher_platforms (list of platforms: FACEBOOK, INSTAGRAM, etc.)
      - search_page_ids (list of Facebook page IDs)
      - search_terms (string; max 100 characters)
      - search_type(enum): KEYWORD_UNORDERED, KEYWORD_EXACT_PHRASE
      - unmask_removed_content (boolean)
      - fields (list of fields to return)
    
    Returns:
        List[Dict[str, Any]]: A detailed list of ad objects, with full output as the API is capable of displaying.

    Notes:
        - All available fields (including "spend", "impressions", etc.) are always requested regardless of ad_type.
        - However, financial data such as "spend", "impressions", and "currency" are only returned by the API when
          ad_type is POLITICAL_AND_ISSUE_ADS.
        - EU-specific fields (e.g. "eu_total_reach") are only returned when at least one EU country is included.
        - The ad_delivery_stop_time field is only returned for INACTIVE ads.
        - When verbose=True, the complete API request parameters are logged in detail.
    """
    
    # Validate required parameters
    if not access_token:
        raise ValueError("access_token is required")
    if not ad_reached_countries:
        raise ValueError("ad_reached_countries is required")
    if ad_type and ad_type not in VALID_AD_TYPES:
        raise ValueError(f"Invalid ad_type. Valid values: {VALID_AD_TYPES}")
    if media_type and media_type not in VALID_MEDIA_TYPES:
        raise ValueError(f"Invalid media_type. Valid values: {VALID_MEDIA_TYPES}")
    if ad_active_status and ad_active_status not in VALID_AD_ACTIVE_STATUS:
        raise ValueError(f"Invalid ad_active_status. Valid values: {VALID_AD_ACTIVE_STATUS}")

    # Always include all available fields if fields parameter is not provided
    if fields is None:
        fields = COMMON_FIELDS + POLITICAL_FIELDS + EU_POLITICAL_FIELDS + INACTIVE_AD_FIELDS
        # Remove any duplicates while preserving order
        fields = list(dict.fromkeys(fields))
    
    # Configure HTTP session with retries
    session = requests.Session()
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    
    # Build base parameters
    params: Dict[str, Union[str, int, bool]] = {
        "access_token": access_token,
        "fields": ",".join(fields or DEFAULT_FIELDS),
        "limit": min(limit_per_request, 100),
        "ad_reached_countries": json.dumps(ad_reached_countries)
    }
    
    # Add optional parameters
    optional_params = {
        "search_terms": search_terms,
        "ad_active_status": ad_active_status,
        "ad_delivery_date_min": ad_delivery_date_min,
        "ad_delivery_date_max": ad_delivery_date_max,
        "ad_type": ad_type,
        "bylines": bylines,
        "delivery_by_region": delivery_by_region,
        "estimated_audience_size_min": estimated_audience_size_min,
        "estimated_audience_size_max": estimated_audience_size_max,
        "languages": languages,
        "media_type": media_type,
        "publisher_platforms": publisher_platforms,
        "search_page_ids": search_page_ids,
        "search_type": search_type,
        "unmask_removed_content": unmask_removed_content
    }
    
    for key, value in optional_params.items():
        if value is not None:
            if isinstance(value, list):
                params[key] = json.dumps(value)
            elif isinstance(value, bool):
                params[key] = "true" if value else "false"
            else:
                params[key] = value

    # Log a warning about data availability based on ad_type
    if ad_type != "POLITICAL_AND_ISSUE_ADS":
        logger.warning("Although financial fields like 'spend' and 'impressions' are requested, "
                    "they will only be returned by the API for political ads. "
                    "Consider setting ad_type to 'POLITICAL_AND_ISSUE_ADS' if you need this data.")
    
    # Detailed output: log all API request parameters if verbose is True
    if verbose:
        logger.info("Detailed API Request Parameters:\n%s", json.dumps(params, indent=2))
    
    # Prepare API endpoint
    base_url = f"https://graph.facebook.com/{api_version}/ads_archive"
    ads_data = []
    page_count = 0
    after_cursor = None

    try:
        while True:
            if max_pages and page_count >= max_pages:
                logger.info("Stopping at max pages limit: %s", max_pages)
                break
            if after_cursor:
                params["after"] = after_cursor
            elif "after" in params:
                del params["after"]

            logger.info("Fetching page %s", page_count + 1)
            if verbose:
                logger.info("Querying URL: %s\nWith parameters:\n%s", base_url, json.dumps(params, indent=2))
            
            response = session.get(base_url, params=params, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            ads_data.extend(data.get("data", []))
            page_count += 1

            if max_results and len(ads_data) >= max_results:
                ads_data = ads_data[:max_results]
                logger.info("Reached max results limit: %s", max_results)
                break

            paging = data.get("paging", {})
            after_cursor = paging.get("cursors", {}).get("after")
            if not after_cursor:
                logger.info("No more pages available")
                break
    except requests.exceptions.HTTPError as e:
        logger.error("HTTP Error: %s - %s", e.response.status_code, e.response.text)
        raise
    except json.JSONDecodeError as e:
        logger.error("JSON parsing error: %s", e)
        raise
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        raise
    finally:
        session.close()

    return ads_data

def get_page_id(page_name: str, access_token: str) -> Optional[str]:
    import requests
    url = f"https://graph.facebook.com/v18.0/{page_name}"
    params = {
        "fields": "id",
        "access_token": access_token
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get('id')
    except Exception as e:
        print(f"Error: {e}")
        return None

def validate_page_info(page_name: str, access_token: str) -> Optional[Dict[str, Any]]:
    import requests
    url = f"https://graph.facebook.com/v18.0/{page_name}"
    params = {
        "fields": "id,name,username,link,verification_status",
        "access_token": access_token
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return {
            'id': data.get('id'),
            'name': data.get('name'),
            'username': data.get('username'),
            'url': data.get('link'),
            'verified': data.get('verification_status') == 'blue_verified'
        }
    except KeyError:
        print("Page not found or access denied")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def batch_lookup(page_names: List[str], access_token: str) -> Dict[str, Optional[str]]:
    import requests
    url = "https://graph.facebook.com/v18.0/"
    params = {
        "ids": ",".join(page_names),
        "fields": "id,name",
        "access_token": access_token
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return {name: info.get('id') for name, info in data.items()}
    except Exception as e:
        print(f"Error: {e}")
        return {}

if __name__ == "__main__":
    # Example usage
    try:
        # Example 1: Standard query (minimal fields)
        ads = fetch_ads(
            ad_reached_countries=["US"],
            search_terms="climate",
            ad_active_status="ALL",
            limit_per_request=50,
            max_pages=1
        )
        
        logger.info("Standard API Response:")
        print(json.dumps(ads, indent=2))
        logger.info("Total ads fetched: %s", len(ads))
        
        # Example 2: Best ads query (using appropriate search parameters for non-political ads)
        ads_best = fetch_ads(
            ad_reached_countries=["US"],
            ad_active_status="ACTIVE",
            ad_delivery_date_min="2023-01-01",
            ad_delivery_date_max="2025-02-28",
            ad_type="ALL",  # Non-political ads
            languages=["en"],
            media_type="VIDEO",
            publisher_platforms=["FACEBOOK", "INSTAGRAM"],
            search_terms="cat food",
            search_type="KEYWORD_EXACT_PHRASE",
            unmask_removed_content=True,
            limit_per_request=50,
            max_pages=2,
            verbose=True
            # Removed: delivery_by_region, estimated_audience_size_min, estimated_audience_size_max
            # These parameters are only valid for POLITICAL_AND_ISSUE_ADS
        )
        
        logger.info("Best Ads Query Response:")
        print(json.dumps(ads_best, indent=2))
        logger.info("Total best ads fetched: %s", len(ads_best))
        
    except Exception as e:
        logger.error("Error during query: %s", e)