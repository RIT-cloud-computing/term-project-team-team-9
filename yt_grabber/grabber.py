import time
import pafy
import cv2
import boto3

def main():    
    client = boto3.resource('s3')
    buffer = client.Bucket('rek-image-buffer')
    
    url = "https://youtu.be/RQA5RcIZlAM"
    video = None
    for _ in range(50):
        try:
            video = pafy.new(url)
            break
        except KeyError:
            print("Could not connect to youtube-dl. Trying again")
            time.sleep(.5)
            # no-op, try again
            pass
        
    if video is None:
        print("Could not connect to youtube-dl after 50 attempts")
        print("This is due to the new youtube api changes removing dislikes, and the py libraries not being updated")
        print("In other words, it's not our fault")
            
    print("video stream retrieved")
    stream = video.getbest()
    capture = cv2.VideoCapture(stream.url)
    while True:
        grabbed, frame = capture.read()
        cv2.imwrite('test.png', frame)
        
        if not grabbed:
            break

        with open('test.png', 'rb') as data:
            buffer.put_object(Body=data, Key=(time.asctime(time.localtime(time.time())) + ".PNG").replace(" ", "").replace(":", ""), ContentType='image/png')

        print('Image sent!')
        time.sleep(5)
        #cv2.imshow("Output", frame)
        capture.set(cv2.CAP_PROP_POS_FRAMES, capture.get(cv2.CAP_PROP_POS_FRAMES) + 150)

        
    capture.release()
    cv2.destroyAllWindows()
    # stream.cancel()
    

if __name__ == "__main__":
    main()