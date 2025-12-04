import boto3

client = boto3.client('s3')

response = client.create_bucket(
    Bucket='shubhradeep91-demo-bucket-4dec',
    CreateBucketConfiguration={
        'LocationConstraint': 'ap-south-1',
        'Tags': [
            {
                'Key': 'name',
                'Value': 'shubhradeep-demo-bucket'
            },
        ]
    }
)