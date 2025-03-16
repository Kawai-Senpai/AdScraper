import requests
import json
import os
import logging
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load ACCESS_TOKEN from environment variable
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
if not ACCESS_TOKEN:
    raise ValueError("ACCESS_TOKEN environment variable is not set")

# Replace with your ad account ID
ad_account_id = os.getenv("AD_ACCOUNT_ID")
if not ad_account_id:
    raise ValueError("AD_ACCOUNT_ID environment variable is not set")

# Endpoint URL
create_url = f'https://graph.facebook.com/v20.0/{ad_account_id}/reachfrequencypredictions'

# Headers
headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

# Current Unix timestamp
current_time = int(time.time())

# Payload for creating a prediction
payload = {
    'objective': 'REACH',
    'start_time': current_time + 86400,  # Campaign starts in 1 day
    'end_time': current_time + 86400 * 8,  # Campaign ends in 8 days
    'frequency_cap': 2,
    'interval_frequency_cap_reset_period': 168,  # 1 week in hours
    'budget': 1000000,  # Budget in cents (e.g., $10,000)
    'prediction_mode': 1,  # Predict reach based on budget
    'target_spec': {
        'geo_locations': {
            'countries': ['US']
        },
        'age_min': 18,
        'age_max': 65,
        'genders': [1, 2],  # 1 for male, 2 for female
        'interests': [{'id': '6003139266461', 'name': 'Technology'}]
    }
}

# Create the prediction
try:
    response = requests.post(create_url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()  # Raise exception for non-200 status codes
    
    prediction_id = response.json().get('id')
    logger.info(f'Prediction ID: {prediction_id}')

    # Check prediction status with explicit fields request
    status_url = f'https://graph.facebook.com/v20.0/{prediction_id}?fields=prediction_progress,status,external_reach,external_impression,frequency_cap'
    
    max_attempts = 15  # Add a limit to avoid infinite loop
    attempts = 0
    
    while attempts < max_attempts:
        attempts += 1
        try:
            status_response = requests.get(status_url, headers=headers)
            status_response.raise_for_status()
            
            status_data = status_response.json()
            prediction_progress = status_data.get('prediction_progress')
            
            if prediction_progress is not None:
                if prediction_progress == 100:
                    logger.info('Prediction complete.')
                    logger.info(json.dumps(status_data, indent=4))
                    break
                else:
                    logger.info(f'Prediction in progress: {prediction_progress}% complete.')
            else:
                logger.warning('prediction_progress field is missing in the response.')
                logger.info('Current response data:')
                logger.info(json.dumps(status_data, indent=4))
                
                # Check for status field which might indicate the prediction state
                status = status_data.get('status')
                if status:
                    logger.info(f'Current status: {status}')
                
                # If we've made multiple attempts and still no prediction_progress, break
                if attempts > 5:
                    logger.warning('Multiple attempts without prediction_progress. Check permissions or wait longer.')
                    break
        except requests.RequestException as e:
            logger.error(f'Error checking prediction status: {e}')
            break
            
        time.sleep(10)  # Wait before checking again
    
    if attempts >= max_attempts:
        logger.warning(f'Reached maximum attempt limit ({max_attempts}) without completion.')
        
except requests.RequestException as e:
    logger.error(f'Error creating prediction: {e}')
    if hasattr(e, 'response') and e.response is not None:
        logger.error(f'Response content: {e.response.text}')