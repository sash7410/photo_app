import boto3
import json
import logging
import requests

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

headers = {"Content-Type": "application/json"}
host = "https://search-photos-5l4vvfb77o22onqn6kixmrg2gi.us-west-2.es.amazonaws.com"
region = 'us-west-2'
lex_v2 = boto3.client('lexv2-runtime', region_name=region)

def lambda_handler(event, context):

    print("EVENT --- {}".format(json.dumps(event)))
    q1 = event["queryStringParameters"]["q"]
    print('nowww')
    print(q1)
    print('now2222')
    if(q1 == "searchAudio"):
        q1 = convert_speechtotext()

    print("q1:", q1)
    labels = get_labels(q1)
    print("labels", labels)
    if len(labels) == 0:
        return
    else:
        img_paths = get_photo_path(labels)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'imagePaths': img_paths,
            'userQuery': q1,
            'labels': labels,
        }),
        'headers': {
            'Access-Control-Allow-Origin': '*'
        },
        "isBase64Encoded": False
    }
    

def get_labels(query):
    # Make sure to replace 'yourBotId', 'yourBotAliasId', and 'yourLocaleId' with your actual bot details
    response = lex_v2.recognize_text(
        botId='HWYJTUQXRC',
        botAliasId='TSTALIASID',
        localeId='en_US',
        sessionId='string',  # Replace 'string' with a unique identifier for the user's session
        text=query
    )
    print("lex-response", response)

    labels = []
    # The structure of the response for Lex V2 is different from V1.
    # Lex V2 uses 'interpretedValues' key under 'slots' to get the slot values
    if 'sessionState' in response and 'intent' in response['sessionState']:
        slots = response['sessionState']['intent'].get('slots', {})
        for key, slot_detail in slots.items():
            # Check if slot has been filled
            if slot_detail and 'value' in slot_detail and 'interpretedValue' in slot_detail['value']:
                value = slot_detail['value']['interpretedValue']
                if value:
                    labels.append(value)
    
    return labels


def get_photo_path(labels):
    img_paths = []
    unique_labels = []
    for x in labels:
        if x not in unique_labels:
            unique_labels.append(x)
    labels = unique_labels
    print("inside get photo path", labels)
    for i in labels:
        path = host + '/_search?q=labels:'+i
        print(path)
        response = requests.get(path, headers=headers,
                                auth=("root", "Root@123"))
        print("response from ES", response)
        dict1 = json.loads(response.text)
        hits_count = dict1['hits']['total']['value']
        print("DICT : ", dict1)
        for k in range(0, hits_count):
            img_obj = dict1["hits"]["hits"]
            img_bucket = dict1["hits"]["hits"][k]["_source"]["bucket"]
            print("img_bucket", img_bucket)
            img_name = dict1["hits"]["hits"][k]["_source"]["objectKey"]
            print("img_name", img_name)
            img_link = 'https://photosbucketb2cc.s3.us-west-2.amazonaws.com' + \
                 '/' + str(img_name)
            print(img_link)
            img_paths.append(img_link)
    print(img_paths)
    return img_paths

