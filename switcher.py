import boto3
import fileinput
import json

def main():
    cdkOutput = open("./cdk/cdk-outputs.json")

    cdkVars = json.load(cdkOutput)

    buffer_bucket = cdkVars["CdkStack"]["BufferBucket"]
    site_bucket = cdkVars["CdkStack"]["HTMLBucket"]
    endpoint = cdkVars["CdkStack"]["API"]
    
    with fileinput.FileInput("./index.html", inplace=True, backup='.bak') as file:
        for line in file:
            print(line.replace("APIEndPoint", endpoint), end='')
    
    with fileinput.FileInput("./yt_grabber/grabber.py", inplace=True, backup='.bak') as file:
        for line in file:
            print(line.replace('rek-image-buffer', buffer_bucket), end='')

    index = open('./index.html')

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(site_bucket)
    bucket.put_object(Body=index, Key='index.html', ContentType='text/html')


if __name__ == "__main__":
    main()