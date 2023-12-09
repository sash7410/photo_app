from variables import *

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

headers = {"Content-Type": "application/json"}
host = ES_URL
region = 'us-east-1'
lex = boto3.client('lex-runtime', region_name=region)


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
    
# def get_labels(query):
#     # Replace 'YourBotAlias' with the alias you deployed your Lex bot to
#     response = lex.post_text(botName='SearchBot', botAlias='$LATEST', userId="string", inputText=query)
#     labels = []
#     if 'slots' in response:
#         for key, value in response['slots'].items():
#             if value:
#                 labels.append(value)
#     return labels


def get_labels(query):
    response = lex.post_text(
        botName='search',
        botAlias='TestBotAlias',
        userId="string",
        inputText=query
    )
    print("lex-response", response)

    labels = []
    if 'slots' not in response:
        print("No photo collection for query {}".format(query))
    else:
        print("slot: ", response['slots'])
        slot_val = response['slots']
        for key, value in slot_val.items():
            if value != None:
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
                                auth=(ES_USER, ES_PASS))
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
            img_link = 'https://s3.amazonaws.com/' + \
                str(img_bucket) + '/' + str(img_name)
            print(img_link)
            img_paths.append(img_link)
    print(img_paths)
    return img_paths


# import json
# import boto3
# import requests

# def lambda_handler(event, context):
#     # Extract query parameter
#     query = event['queryStringParameters']['q']
#     print(query)

#     # Initialize Lex client
#     lex_client = boto3.client('lex-runtime', region_name='us-east-1')  # Replace with your region

#     # Send input to Lex and get a response
#     lex_response = lex_client.post_text(
#         botName='SearchBot',  # Replace with your Lex bot name
#         botAlias='Prod',   # Replace with your Lex bot alias
#         userId='userID',           # A user ID for the chat
#         inputText='show me photos of cat'
#     )

#     # Check if keywords are returned from Lex
#     if 'slots' in lex_response:
#         slots = lex_response['slots']
#         keywords = [value for value in slots.values() if value]

#         if keywords:
#             # Elasticsearch query
#             query = {
#                 "query": {
#                     "match": {
#                         "keywords": " ".join(keywords)
#                     }
#                 }
#             }
#             url = 'https://search-myphotos1-7aduclkckt6r6ayol6deekjtny.us-east-1.es.amazonaws.com'  # Replace with your Elasticsearch URL
#             headers = {"Content-Type": "application/json"}

#             # Elasticsearch credentials
#             es_username = 'Master'  # Replace with your Elasticsearch master username
#             es_password = 'Master@123'  # Replace with your Elasticsearch master password

#             # Perform the search
#             response = requests.get(url, headers=headers, json=query, auth=(es_username, es_password))

#             if response.status_code == 200:
#                 # Extract and return results
#                 es_response = response.json()
#                 results = [doc['_source'] for doc in es_response['hits']['hits']]
#                 return {
#                     'statusCode': 200,
#                     'body': json.dumps(results)
#                 }
#             else:
#                 # Handle HTTP errors
#                 return {
#                     'statusCode': response.status_code,
#                     'body': json.dumps({"error": "Elasticsearch query failed"})
#                 }
#         else:
#             # Return empty array if no keywords found
#             return {
#                 'statusCode': 200,
#                 'body': json.dumps([])
#             }
#     else:
#         # Handle case where Lex response does not contain expected slots
#         return {
#             'statusCode': 500,
#             'body': json.dumps({"error": "Invalid response from Lex"})
#         }