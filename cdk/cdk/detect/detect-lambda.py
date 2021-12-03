import json
import boto3
import time;

def lambda_handler(event, context):
    imageTime = time.time()
    
    #
    originS3 = event["Records"][0]["s3"]["bucket"]["name"]
    originKey = event["Records"][0]["s3"]["object"]["key"]
    print(originKey, originS3)
    # Get Rek data
    rek = boto3.client('rekognition')
    labels = rek.detect_labels(
        Image={
            'S3Object': {
                'Bucket': originS3, 
                'Name': originKey
            }
        },
        MaxLabels=150
    )
    
    for label in labels["Labels"]:
        if label["Name"] == "Person":
            people = label["Instances"]
    
    # Jaywalking zone (expects 1920 x 1080)
    # Slope (px values)
    m = 0.79881656804734
    # y intercept (px values)
    b = -185.32544378698
    
    jaywalkers = []
    walkers = []
    
    # Compare each person against bounding line
    for person in people:
        actual_bottom = 1080 - person["BoundingBox"]["Top"] * 1080
        actual_left = person["BoundingBox"]["Left"] * 1920
        y = m * actual_left + b
        # Sort those above the line as jaywalker and below as 
        if (actual_bottom > y and actual_left > 500):
            jaywalkers.append(person)
        else:
            walkers.append(person)
    print(len(jaywalkers))
    if (len(jaywalkers) > 0):
        # Save to S3 (requires S3/intergration)
        s3 = boto3.resource('s3')
        copy_source = {
            'Bucket': originS3,
            'Key': originKey
        }
        s3.meta.client.copy(copy_source, os.environ['DETECT_BUCKET'], originKey)
        
        s3client = boto3.client('s3')
        my_session = boto3.session.Session()
        my_region = my_session.region_name
    
        url = "https://{}.s3.{}.amazonaws.com/{}".format(os.environ['DETECT_BUCKET'], my_region, originKey)
    
        # Save to database (requires DB/intergration)
        
        jaywalkerArray = []
        for jaywalker in jaywalkers:
            boundMap = {} 
            for val in jaywalker["BoundingBox"]:
                boundMap[val] = {"S": str(jaywalker["BoundingBox"][val])}
            jaywalkerArray.append({"M": boundMap})
        
        walkerArray = []
        for walker in walkers:
            boundMap = {} 
            for val in walker["BoundingBox"]:
                boundMap[val] = {"S": str(walker["BoundingBox"][val])}
            walkerArray.append({"M": boundMap})
        
        db = boto3.client('dynamodb')
        db.put_item(
            TableName=os.environ["DY_TABLE"],
            Item={
                "submit": {
                    "S": "OK"
                },
                "epochtime": {
                    "S": str(imageTime),
                },
                "Image": {
                    "S": url,
                },
                "Jaywalkers": {
                    "L": jaywalkerArray,
                },
                "Walkers": {
                    "L": walkerArray,
                }
            }
        )
        
        #Send to SNS Lambda (Working)
        snsLambda = boto3.client('lambda')
    
        inputParams = {
            'jaywalkers': jaywalkers,
            'walkers': walkers,
            'time': imageTime,
            'image': url
        }
        
        snsLambda.invoke(
            FunctionName = os.environ['SNS_LAMBDA'],
            InvocationType = 'Event',
            Payload = json.dumps(inputParams)
        )
