import json
import os
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from boto3.dynamodb.conditions import Key
from botocore.vendored import requests

REGION = 'us-east-1'
HOST = 'search-restaurants-y27a5vsjdaqx4zafopncw2nvkq.us-east-1.es.amazonaws.com'
INDEX = 'restaurants'
db = boto3.resource('dynamodb').Table('Yelp-restaurants')

def query(term):
    q = {'size': 3, 'query': {'multi_match': {'query': term}}}

    client = OpenSearch(hosts=[{
        'host': HOST,
        'port': 443
    }],
                        http_auth=get_awsauth(REGION, 'es'),
                        use_ssl=True,
                        verify_certs=True,
                        connection_class=RequestsHttpConnection)

    res = client.search(index=INDEX, body=q)
    print(res)

    hits = res['hits']['hits']
    results = []
    for hit in hits:
        results.append(hit['_source'])

    return results

def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)

def queryDynamo(ids):
    results = []
    for id in ids:
        print(id)
        response = db.query(KeyConditionExpression = Key("Business ID").eq(id))
        print(response)
        results.append(response["Items"][0])
    return results

def lambda_handler(event, context):
    sqs_queue_url = 'https://sqs.us-east-1.amazonaws.com/956075594925/message'

    # Receive a message from the SQS queue
    sqs = boto3.client('sqs')
    response = sqs.receive_message(
        QueueUrl=sqs_queue_url,
        AttributeNames=[
            'All'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )

    d = response['Messages'][0]
    msg_body = json.loads(d['Body'])
    print('This is message body', msg_body)

    if 'Messages' in response:
        # Extract the message body from the received message
        message = msg_body

        # Extract data from the message slots
        city = msg_body.get('City')
        cuisine = msg_body.get('Cuisine')
        date = msg_body.get('Date')
        people = msg_body.get('People')
        time = msg_body.get('Time')
        email = 'quanyi306@gmail.com'

        # getting the message from the open source
        query_resp = query(cuisine)
        print('QUERY: ', query_resp)

        ids = []
        for i in range(len(query_resp)):
            ids.append(query_resp[i]['Restaurant'])
        print(ids)

        # pulling the restaurant information from the dynamoDB
        db_rest = queryDynamo(ids)
        print(db_rest[0]['CuisineType']['S'])

        # sending the confirmation to the email
        client = boto3.client("ses")
        subject = "Reservation Details"

        # Create the HTML body using the data from the message slots
        body = f"""
        <html>
            <body>
                <h2>Reservation Details:</h2>
                <p>Hello,</p>
                <p>You have made a reservation for <strong>{people} people</strong> at <strong>{time}</strong> in <strong>{city}</strong> on <strong>{date}</strong> for <strong>{cuisine} cuisine</strong>.</p>
                <p>Here are some restaurant suggestions:</p>
                <ul>
        """

        for i in range(0,3): 
            body += f"<li><strong>{db_rest[i]['Name']}</strong> located at {db_rest[i]['Address']}</li>"

        body += """
                </ul>
                <p>Enjoy your meal!</p>
            </body>
        </html>
        """

        print(body)

        # Send the email
        email_response = client.send_email(
            Source="quanyi306@gmail.com",
            Destination={"ToAddresses": [email]},
            Message={"Subject": {"Data": subject}, "Body": {"Html": {"Data": body}}}
        )
        
        return email_response
    
    else:
        return "No messages in the queue."

