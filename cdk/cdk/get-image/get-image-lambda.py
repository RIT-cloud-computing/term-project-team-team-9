import boto3
import json

def lambda_handler(event, context):
	client = boto3.client('dynamodb')
	resp = client.query(
		TableName='jaywalker',
		ProjectionExpression="Image,Jaywalkers,Walkers",
		Limit=5,
		KeyConditionExpression='submit=:val',
		ExpressionAttributeValues={":val": {"S": "OK"}},
		ScanIndexForward=False
	)
	
	ret = []
	items = resp["Items"]
	for item in items:
		url = item["Image"]["S"]
		walker_count = 0
		jaywalker_count = 0
		if "Walkers" in item:
				walker_count = len(item["Walkers"]["L"])
		if "Jaywalkers" in item:
				jaywalker_count = len(item["Jaywalkers"]["L"])
		ret.append({
				"url": url,
				"walkers": walker_count,
				"jaywalkers": jaywalker_count
		})
			
			

	return ret
