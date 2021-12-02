from aws_cdk import (
    core as cdk,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_dynamodb as ddb,
    aws_s3_notifications as s3_notifications,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions
)


class CdkStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # create new IAM group and user
        group = iam.Group(self, "RekGroup")
        user = iam.User(self, "RekUser")

        # add IAM user to the new group
        user.add_to_group(group)

        # create S3 bucket to hold images
        # give new user access to the bucket
        temp_bucket = s3.Bucket(self, 'rek-image-buffer')
        temp_bucket.grant_read_write(user)

        # create S3 bucket to hold images
        # give new user access to the bucket
        bucket = s3.Bucket(self, 'rek-image-detect')
        bucket.grant_read_write(user)

        # create DynamoDB table to hold Rekognition results
        table = ddb.Table(
            self, 'jaywalker',
            partition_key={'name': 'Image', 'type': ddb.AttributeType.STRING},
            sort_key={'name': 'Date', 'type': ddb.AttributeType.STRING}
        )

        # create Sns Topic
        sns_topic = sns.Topic(self, "sns-notif")
        email_address = cdk.CfnParameter(self, "email-param")
        sns_topic.add_subscription(subscriptions.EmailSubscription(email_address.value_as_string))

        # create Lambda function
        sns_lambda = _lambda.Function(
            self, 'sns-lambda',
            runtime = _lambda.Runtime.PYTHON_3_9,
            handler = 'sns-lambda.lambda_handler',
            code = _lambda.Code.from_asset('cdk/sns')
        )

        # create Lambda function
        detect_lambda = _lambda.Function(
            self, 'Test-detect',
            runtime = _lambda.Runtime.PYTHON_3_9,
            handler = 'test-detect.lambda_handler',
            code = _lambda.Code.from_asset('cdk/detect')
        )

        # add Rekognition permissions for Lambda function
        statement = iam.PolicyStatement()
        statement.add_actions("rekognition:DetectLabels")
        statement.add_resources("*")
        detect_lambda.add_to_role_policy(statement)

        # create trigger for Lambda function with image type suffixes
        notification = s3_notifications.LambdaDestination(detect_lambda)
        notification.bind(self, bucket)
        bucket.add_object_created_notification(notification, s3.NotificationKeyFilter(suffix='.png'))

        # grant permissions for lambda to read/write to DynamoDB table and bucket
        table.grant_read_write_data(detect_lambda)
        bucket.grant_read_write(detect_lambda)

