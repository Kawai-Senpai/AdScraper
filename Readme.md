# Meta Ad Library API Field Availability Guide

This document explains the complex field availability patterns in Meta's Ad Library API and provides guidance on how to maximize data retrieval.

## Field Availability Categories

Meta's Ad Library has different field availability based on multiple factors:

### 1. Always Available Fields

These fields are available for all ad types with minimal restrictions:

- `id`, `ad_creation_time`, `ad_snapshot_url`
- `ad_creative_bodies`, `ad_creative_link_captions`, `ad_creative_link_descriptions`, `ad_creative_link_titles`
- `ad_delivery_start_time`
- `bylines`, `languages`
- `page_id`, `page_name`
- `publisher_platforms`
- `target_ages`, `target_gender`, `target_locations`

### 2. Political Ad Only Fields

These fields are **only available** when using `ad_type=POLITICAL_AND_ISSUE_ADS`:

- `spend`
- `impressions`
- `currency`
- `estimated_audience_size`
- `demographic_distribution`
- `delivery_by_region`

### 3. EU-Targeted Political Ad Fields

These fields require both political ad classification AND targeting EU countries:

- `eu_total_reach`

### 4. Inactive Ad Only Fields

These fields only appear for completed campaigns:

- `ad_delivery_stop_time` (only for ads with `ad_active_status=INACTIVE`)

### 5. Conditionally Available Fields

These fields have complex availability rules based on multiple factors:

- `age_country_gender_reach_breakdown`: Requires political classification + sufficient audience size

## Technical Explanation of Field Limitations

### Financial Data (spend, impressions)

Meta's policy is to only expose financial data for ads classified as political or issue ads. This is a policy decision rather than a technical limitation. When requesting these fields:

- For non-political ads: These fields will be `null` or missing entirely
- For political ads with small spend (<$100): Values may still be `null`
- For political ads with significant spend: Values are typically provided

```python
# To get financial data:
params = {
    "ad_type": "POLITICAL_AND_ISSUE_ADS",
    "fields": ["spend", "impressions", "currency"]
}
```

### Regional Reach Data

The `eu_total_reach` field is a unique case that requires:
1. Political ad classification (`ad_type=POLITICAL_AND_ISSUE_ADS`)
2. At least one EU country in the targeting parameters

```python
# To get EU reach data:
params = {
    "ad_type": "POLITICAL_AND_ISSUE_ADS",
    "ad_reached_countries": ["DE", "FR"],  # EU countries
    "fields": ["eu_total_reach"]
}
```

### Demographic Data

Full demographic distribution has the strictest requirements:

1. Political ad classification
2. Sufficient audience size (typically >1000 impressions)
3. In some cases, special API access for research

```python
# Request for demographic data:
params = {
    "ad_type": "POLITICAL_AND_ISSUE_ADS",
    "fields": ["demographic_distribution"]
}
```

### Temporal Data

The `ad_delivery_stop_time` field is only present for concluded ad campaigns:

```python
# To get delivery stop time:
params = {
    "ad_active_status": "INACTIVE",
    "fields": ["ad_delivery_stop_time"]
}
```

## Best Practices for Maximum Data Retrieval

1. **Query Political Ads for Financial Data**
   ```python
   params = {
       "ad_type": "POLITICAL_AND_ISSUE_ADS",
       "search_terms": "election"
   }
   ```

2. **Split Queries by Status** - Create separate queries for active and inactive ads
   ```python
   # For active ads
   params_active = {"ad_active_status": "ACTIVE"}
   
   # For inactive ads (with delivery stop time)
   params_inactive = {"ad_active_status": "INACTIVE"}
   ```

3. **Optimize Field Requests** - Only request fields that are likely to be available based on other parameters
   ```python
   # Use the utility functions in field_utils.py
   from field_utils import get_optimized_fields
   
   fields = get_optimized_fields(
       ad_type="POLITICAL_AND_ISSUE_ADS",
       ad_active_status="ALL",
       ad_reached_countries=["US", "DE"]
   )
   ```

4. **Analyze Missing Fields** - Use the utility to understand why fields are missing
   ```python
   from field_utils import explain_missing_fields
   
   explanations = explain_missing_fields(ads, requested_fields)
   ```

## Field Obfuscation Patterns

Meta implements several obfuscation patterns that affect field availability:

1. **Thresholds**: Small values for impressions, spend, etc. are often nullified
2. **Aggregation**: Demographic data is often aggregated to protect user privacy
3. **Range Values**: Some numeric values may be presented as ranges rather than specific values
4. **Missing Fields**: Instead of returning null values, fields may be completely omitted

These patterns are by design and generally cannot be circumvented through API parameters.

## Advanced Access Requirements

For academic or research purposes requiring more detailed data, Meta offers a special research access program:

- Apply through their Academic Research hub
- Requires institutional affiliation 
- Process involves explaining the research purpose and signing additional terms
- May grant access to more granular demographic and spending data

## API Tier Differences

Meta's API access is organized into tiers that affect field availability:

1. **Standard Access**: Basic fields only
2. **Extended Access**: Includes some political ad data
3. **Research Access**: Most comprehensive data access

Your access token determines which tier you have access to, which further affects field availability regardless of parameters used.

# Full API Capabilities and Detailed Parameter Exposure

The fetch_ads function now exposes every search parameter available through the Meta Ad Library API.
Below is a summary of all the parameters you can use:

- **ad_active_status:** enum {ACTIVE, ALL, INACTIVE} – Defaults to ACTIVE; use ALL or INACTIVE to include more.
- **ad_delivery_date_min / ad_delivery_date_max:** string (YYYY-mm-dd) – Define the boundaries of ad delivery dates.
- **ad_reached_countries:** array – Required list of ISO country codes; ads not reaching an EU country will be returned only if they are about social issues, elections, or politics.
- **ad_type:** enum {ALL, EMPLOYMENT_ADS, FINANCIAL_PRODUCTS_AND_SERVICES_ADS, HOUSING_ADS, POLITICAL_AND_ISSUE_ADS} – Filter by ad category.
- **bylines:** array – Provide full bylines to filter political ads.
- **delivery_by_region:** array – Specify regions (states or provinces) to restrict the ad search.
- **estimated_audience_size_min / estimated_audience_size_max:** int – Use approved boundary values.
- **languages:** array – List of ISO 639-1 codes (also supports certain ISO 639-3 codes).
- **media_type:** enum {ALL, IMAGE, MEME, VIDEO, NONE} – Specify the type of media present in the ad.
- **publisher_platforms:** array – Filter ads by the platform(s) where they appeared.
- **search_page_ids:** array – Filter by specific Facebook page IDs.
- **search_terms:** string – Text to search within ad creatives (max 100 characters).
- **search_type:** enum {KEYWORD_UNORDERED, KEYWORD_EXACT_PHRASE} – Determines how search_terms are matched.
- **unmask_removed_content:** boolean – If true, reveals ads removed for standards violations.

Additionally, if verbose logging is enabled in fetch_ads, all parameters and request details are printed, enabling you to see exactly how the API call is constructed. This detailed output assists in debugging, thorough analysis, and in understanding the full capabilities of the Meta Ad Library API.
