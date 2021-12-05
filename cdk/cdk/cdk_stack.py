from aws_cdk import (
    core as cdk,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_dynamodb as ddb,
    aws_s3_notifications as s3_notifications,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_apigateway as apigateway
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
        bucket = s3.Bucket(self, 'rek-image-detect', public_read_access=True)
        bucket.grant_read_write(user)

        # HTML bucket
        html_bucket = s3.Bucket(self, 'html-bucket', website_index_document="index.html", public_read_access=True)
        html_bucket.grant_read_write(user)

        # create DynamoDB table to hold Rekognition results
        table = ddb.Table(
            self, 'jaywalker',
            partition_key={'name': 'Submit', 'type': ddb.AttributeType.STRING},
            sort_key={'name': 'epochtime', 'type': ddb.AttributeType.STRING}
        )

        # create API gateway
        api = apigateway.RestApi(self, 'get-image-api',
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=["GET"],
                allow_headers=apigateway.Cors.DEFAULT_HEADERS
            )
        )
        url = api.url + "/default/get-resource"

        # create Lambda function for frontend
        image_lambda = _lambda.Function(
            self, 'get-image',
            runtime = _lambda.Runtime.PYTHON_3_9,
            handler = 'get-image-lambda.lambda_handler',
            code = _lambda.Code.from_asset('cdk/get-image'),
            environment = {
                "DY_TABLE": table.table_name
            }
        )

        statement = iam.PolicyStatement()
        statement.add_actions("s3:*")
        statement.add_resources("*")
        image_lambda.add_to_role_policy(statement)

        resource = api.root.add_resource("get-resource", default_cors_preflight_options=apigateway.CorsOptions(
            allow_origins=["*"]))
        resource.add_method("GET", apigateway.LambdaIntegration(image_lambda, proxy=False, integration_responses=[apigateway.IntegrationResponse(
                status_code="200", response_parameters={"method.response.header._access-_control-_allow-_origin": "'*'"})])
                , method_responses=[apigateway.MethodResponse(status_code="200", response_parameters={
            "method.response.header._content-_type": True,
            "method.response.header._access-_control-_allow-_origin": True,
            "method.response.header._access-_control-_allow-_credentials": True
        })])

        # create Sns Topic
        # npx cdk deploy my-stack-name    \
        #    --parameters myFirstParameter=value1 \
        #    --parameters mySecondParameter=value=2

        sns_topic = sns.Topic(self, "sns-notif")
        email_address = cdk.CfnParameter(self, "email-param")
        sns_topic.add_subscription(subscriptions.EmailSubscription(email_address.value_as_string))

        # create Lambda function
        sns_lambda = _lambda.Function(
            self, 'sns-lambda',
            runtime = _lambda.Runtime.PYTHON_3_9,
            handler = 'sns-lambda.lambda_handler',
            code = _lambda.Code.from_asset('cdk/sns'),
            environment = {
                "SNS_TOPIC": sns_topic.topic_arn
            }
        )

        # create Lambda function
        detect_lambda = _lambda.Function(
            self, 'Test-detect',
            runtime = _lambda.Runtime.PYTHON_3_9,
            handler = 'detect-lambda.lambda_handler',
            code = _lambda.Code.from_asset('cdk/detect'),
            environment = {
                "DETECT_BUCKET": bucket.bucket_name,
                "DY_TABLE": table.table_name,
                "SNS_LAMBDA": sns_lambda.function_arn
            }
        )
        
        statement = iam.PolicyStatement()
        statement.add_actions("dynamodb:*")
        statement.add_resources("*")
        image_lambda.add_to_role_policy(statement)

        # add permissions for dynamo Lambda function
        statement = iam.PolicyStatement()
        statement.add_actions("dynamodb:*")
        statement.add_resources("*")
        image_lambda.add_to_role_policy(statement)

        # add permissions for SNS Lambda function
        statement = iam.PolicyStatement()
        statement.add_actions("sns:*")
        statement.add_resources("*")
        sns_lambda.add_to_role_policy(statement)

        # add permissions for Detect Lambda function
        statement = iam.PolicyStatement()
        statement.add_actions("rekognition:DetectLabels")
        statement.add_resources("*")
        detect_lambda.add_to_role_policy(statement)

        statement = iam.PolicyStatement()
        statement.add_actions("s3:*")
        statement.add_resources("*")
        detect_lambda.add_to_role_policy(statement)

        statement = iam.PolicyStatement()
        statement.add_actions("dynamodb:*")
        statement.add_resources("*")
        detect_lambda.add_to_role_policy(statement)

        statement = iam.PolicyStatement()
        statement.add_actions("lambda:*")
        statement.add_resources("*")
        detect_lambda.add_to_role_policy(statement)

        # create trigger for Lambda function with image type suffixes
        notification = s3_notifications.LambdaDestination(detect_lambda)
        notification.bind(self, temp_bucket)
        temp_bucket.add_object_created_notification(notification, s3.NotificationKeyFilter(suffix='.PNG'))

        # grant permissions for lambda to read/write to DynamoDB table and bucket
        # table.grant_read_write_data(detect_lambda)
        # bucket.grant_read_write(detect_lambda)
        cdk.CfnOutput(self, "BufferBucket", value=temp_bucket.bucket_name)
        cdk.CfnOutput(self, "HTMLBucket", value=html_bucket.bucket_name)
        cdk.CfnOutput(self, "API", value=api.url)
