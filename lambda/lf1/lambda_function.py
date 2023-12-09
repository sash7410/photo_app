import boto3
import json
import requests


def update_elasticsearch_index(index_name, document):
    es.index(index=index_name, body=document)

def lambda_handler(event, context):
    # Retrieve information about the uploaded image from the S3 event
    s3_bucket = event['Records'][0]['s3']['bucket']['name']
    s3_object_key = event['Records'][0]['s3']['object']['key']
    # Initialize Rekognition client
    rekognition = boto3.client('rekognition')
    # Extract S3 object metadata

    # Call detectLabels method
    response = rekognition.detect_labels(
        Image={
            'S3Object': {
                'Bucket': s3_bucket,
                'Name': s3_object_key
            }
        },
        MaxLabels=10,  # Maximum number of labels to return (adjust as needed)
        MinConfidence=75  # Minimum confidence level for detected labels (adjust as needed)
    )
    
    # Process the response - extract and handle labels
    labels = [label['Name'] for label in response['Labels']]
    print(labels)
    # You can further process or store these labels as needed (e.g., in a database or another AWS service)
    # Initialize S3 client
    s3 = boto3.client('s3')
    # Retrieve S3 object metadata
    try:
        response = s3.head_object(Bucket=s3_bucket, Key=s3_object_key)
        print(response)
        created_timestamp = response['LastModified']
        created_timestamp = created_timestamp.isoformat()
        # Check if x-amz-meta-customLabels field exists in metadata
        # If x-amz-meta-customLabels field exists, create a JSON array

        if 'customlabels' in response['Metadata']:
            # labels_array = response['Metadata']['customlabels']
            # Process or utilize labels_array as needed
            custom_labels_string = response['Metadata']['customlabels']
            custom_labels_array = custom_labels_string.split(',')
            labels.extend(custom_labels_array)
            json_object = {
            "objectKey": s3_object_key,
            "bucket": s3_bucket,
            "createdTimestamp": created_timestamp,
            "labels": labels
            }
        else:
            print("No custom labels metadata found.")
            json_object = {
            "objectKey": s3_object_key,
            "bucket": s3_bucket,
            "createdTimestamp": created_timestamp,
            "labels": labels
            }
        auth = ("root", "Root@123")
        index_name = "photosidx"
        elasticsearch_url = "https://search-photos-5l4vvfb77o22onqn6kixmrg2gi.us-west-2.es.amazonaws.com"
        url = f"{elasticsearch_url}/{index_name}/_doc/{s3_object_key}"
        json_object = json.dumps(json_object)
        print(json_object)
        response = requests.post(url, data=json_object, auth=auth, headers={"Content-Type": "application/json"})
        
        print(response)
        print("Response status code:", response.status_code)
        print("Response headers:", response.headers)
        print("Response content:", response.content.decode('utf-8'))
    except Exception as e:
        print("Error retrieving metadata:", e)
        return {
            'statusCode': 500,
            'body': "Error retrieving metadata."
        }
    return {
        'statusCode': 200,
        'body': labels  # Sending labels as the response
    }