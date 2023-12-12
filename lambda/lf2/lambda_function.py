import boto3
import json
import logging
import requests

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Constants for the Elasticsearch service and Lex V2 client
HEADERS = {"Content-Type": "application/json"}
ES_HOST = "https://search-photos-5l4vvfb77o22onqn6kixmrg2gi.us-west-2.es.amazonaws.com"
REGION = 'us-west-2'
lex_client = boto3.client('lexv2-runtime', region_name=REGION)


def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    user_query = get_query_from_event(event)
    
    if is_search_audio_request(user_query):
        user_query = convert_speech_to_text()  
    
    
    labels = extract_labels_from_lex(user_query)
    
    if not labels:
        logger.info("No labels extracted from query.")
        return build_response(200, {"message": "No labels found"})
    
    image_paths = fetch_image_paths_from_elasticsearch(labels)
    return build_response(200, {
        'imagePaths': image_paths,
        'userQuery': user_query,
        'labels': labels,
    })

def get_query_from_event(event):
    return event.get("queryStringParameters", {}).get("q", "")

def is_search_audio_request(query):
    return query.lower() == "searchaudio"

def convert_speech_to_text():
    # Placeholder for speech to text conversion logic
    return "converted text"

def extract_labels_from_lex(query):
    response = lex_client.recognize_text(
        botId='HWYJTUQXRC',
        botAliasId='TSTALIASID',
        localeId='en_US',
        sessionId='uniqueSessionId',  # Replace with a unique identifier for the user's session
        text=query
    )
    logger.info(f"Lex response: {response}")
    
    return get_labels_from_lex_response(response)

def get_labels_from_lex_response(response):
    extracted_labels = []
    slots = response.get('sessionState', {}).get('intent', {}).get('slots', {})
    for slot_detail in slots.values():
        if slot_detail and slot_detail.get('value'):
            value = slot_detail['value'].get('interpretedValue')
            if value:
                extracted_labels.append(value)
    return extracted_labels

def fetch_image_paths_from_elasticsearch(labels):
    unique_labels = list(set(labels))  # Removes duplicates
    logger.info(f"Unique labels for image search: {unique_labels}")
    return [image_url for label in unique_labels for image_url in get_image_urls_for_label(label)]

def get_image_urls_for_label(label):
    search_path = f"{ES_HOST}/_search?q=labels:{label}"
    logger.info(f"Search path: {search_path}")
    response = requests.get(search_path, headers=HEADERS, auth=("root", "Root@123"))
    search_results = response.json()
    logger.info(f"Response from Elasticsearch: {response}")
    
    return build_image_urls_from_search_results(search_results)

def build_image_urls_from_search_results(search_results):
    image_urls = []
    for hit in search_results["hits"]["hits"]:
        object_key = hit["_source"]["objectKey"]
        image_url = f'https://photosbucketb2cc.s3.{REGION}.amazonaws.com/{object_key}'
        logger.info(f"Image URL: {image_url}")
        image_urls.append(image_url)
    return image_urls

def build_response(status_code, body):
    return {
        'statusCode': status_code,
        'body': json.dumps(body),
        'headers': {'Access-Control-Allow-Origin': '*'},
        "isBase64Encoded": False
    }
