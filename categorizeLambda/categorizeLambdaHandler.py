import json

def handler(event, context):
    message = event.get('message', 'No message provided')
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Hello from Lambda! {message}',
        })
    }