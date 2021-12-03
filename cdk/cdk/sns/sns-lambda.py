import json
import boto3

def lambda_handler(event, context):
    message = ""
    # message = message + "Jaywalkers:\n"
    # for jaywalker in event["jaywalkers"]:
    #     message = message + jaywalker + '\n'
    # message = message + "Walkers:\n"
    # for walker in event["walkers"]:
    #     message = message + walker + '\n'
    message = message + "At " + str(event["time"]) + " there were:\n"
    message = message + "Num Jaywalkers- " + str(len(event["jaywalkers"])) + '\n'
    message = message + "Num Walkers- " + str(len(event["walkers"])) + '\n'
    message = message + event["image"]
    print(message)
    client = boto3.client('sns')
    response = client.publish(
        TargetArn=os.environ["SNS_TOPIC"],
        # Message=json.dumps({'default': json.dumps(message)}),
        Message=message,
        MessageStructure='String'
    )