from time import sleep
import pafy
import cv2
import boto3
from botocore.config import Config
import json
import zlib
import base64
import numpy as np
from io import BytesIO
import time

def main():
    config = Config(region_name='us-east-2')
    
    client = boto3.client(
        's3',
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
        capture.set(cv2.CAP_PROP_POS_FRAMES, capture.get(cv2.CAP_PROP_POS_FRAMES) + 150)
            
        with open('test.png', 'rb') as data:
            client.upload_fileobj(data, 'rek-image-buffer', (time.asctime(time.localtime(time.time())) + ".PNG").replace(" ", "").replace(":", ""))

        print('Image sent!')
        sleep(5)

        
    capture.release()
    cv2.destroyAllWindows()
    # stream.cancel()
    

if __name__ == "__main__":
    main()