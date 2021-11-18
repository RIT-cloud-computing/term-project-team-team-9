from time import sleep
import pafy
import cv2
import boto3
from botocore.config import Config
import json
import zlib
import base64

def main():
    config = Config(region_name='us-east-2')
    
    client = boto3.client(
        'lambda',
        config=config
    )
    
    url = "https://youtu.be/RQA5RcIZlAM"
    video = pafy.new(url)
    stream = video.getbest()
    capture = cv2.VideoCapture(stream.url)
    while True:
        grabbed, frame = capture.read()
        cv2.imwrite('test.png', frame)
        
        if not grabbed:
            break
        
        #cv2.imshow("Output", frame)
        capture.set(cv2.CAP_PROP_POS_FRAMES, capture.get(cv2.CAP_PROP_POS_FRAMES) + 30)
            
        response = client.invoke(
            FunctionName='Test-detect',
            Payload=json.dumps(base64.b64encode(zlib.compress(frame.tobytes())).decode('utf-8'))
        )
        print(response)
        sleep(5)

        
    capture.release()
    cv2.destroyAllWindows()
    # stream.cancel()
    

if __name__ == "__main__":
    main()