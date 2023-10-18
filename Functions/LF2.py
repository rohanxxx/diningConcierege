import json
import boto3

dynamodb = boto3.resource('dynamodb')
table_name = 'Yelp-restaurants'

def lambda_handler(event, context):
    try:
        table = dynamodb.Table(table_name)
        
        with open('yelp-data.json') as json_file:
            data = json.load(json_file)
            for item in data:
                table.put_item(Item=item)
        
        return {
            'statusCode': 200,
            'body': 'Data inserted into DynamoDB successfully'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }
