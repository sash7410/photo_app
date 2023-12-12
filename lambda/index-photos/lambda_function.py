import boto3
import json
import requests
import base64
import logging

def initialize_clients():
    return boto3.client('s3'), boto3.client('rekognition')

def fetch_image_from_s3(s3_client, bucket_name, object_key):
    image_response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    return base64.b64decode(image_response['Body'].read())


def analyze_image_with_rekognition(rekognition_client, image_content):
    rekognition_response = rekognition_client.detect_labels(
        Image={'Bytes': image_content},
        MinConfidence=80
    )
    return [label['Name'] for label in rekognition_response['Labels']]

def get_s3_object_metadata(s3_client, bucket_name, object_key):
    return s3_client.head_object(Bucket=bucket_name, Key=object_key)

def update_es_index(elasticsearch_url, index_name, document_id, document):
    url = f"{elasticsearch_url}/{index_name}/_doc/{document_id}"
    response = requests.post(url, data=json.dumps(document), auth=("root", "Root@123"), headers={"Content-Type": "application/json"})
    logging.info(f"ES Update Response: {response.status_code}, Content: {response.content.decode('utf-8')}")

def lambda_handler(event, context):
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting Lambda Handler")

    # Extract S3 bucket and object information from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    logging.info(f"Processing S3 Object: {object_key} in Bucket: {bucket_name}")

    # Initialize AWS clients
    s3_client, rekognition_client = initialize_clients()

    # Fetching and analyzing the image
    image_content = fetch_image_from_s3(s3_client, bucket_name, object_key)
    labels_detected = analyze_image_with_rekognition(rekognition_client, image_content)
    logging.info(f"Detected Labels: {labels_detected}")

    # Retrieve S3 object metadata
    try:
        object_metadata = get_s3_object_metadata(s3_client, bucket_name, object_key)
        creation_timestamp = object_metadata['LastModified'].isoformat()

        if 'customlabels' in object_metadata['Metadata']:
            custom_labels = object_metadata['Metadata']['customlabels'].split(',')
            labels_detected.extend(custom_labels)

        es_document = {
            "objectKey": object_key,
            "bucket": bucket_name,
            "createdTimestamp": creation_timestamp,
            "labels": labels_detected
        }

        # Update Elasticsearch index
        es_index_name = "photosidx"
        es_url = "https://search-photos-5l4vvfb77o22onqn6kixmrg2gi.us-west-2.es.amazonaws.com"
        update_es_index(es_url, es_index_name, object_key, es_document)

    except Exception as error:
        logging.error(f"Error retrieving metadata: {error}")
        return {'statusCode': 500, 'body': "Error retrieving metadata."}

    return {'statusCode': 200, 'body': labels_detected}
