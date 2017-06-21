import numpy as np
import cv2

cap1 = cv2.VideoCapture(1)
cap2 = cv2.VideoCapture(2)


cv2.namedWindow("Merged Images")
#cv2.namedWindow("Cam1")
#cv2.namedWindow("Cam2")

MergedImage = np.zeros((480,1280,3), np.uint8)

while(True):
    # Capture frame-by-frame
 
    while (True):
        ret, frame1 = cap1.read()
        ret, frame2 = cap2.read()

	MergedImage[0:480, 0:640]=frame1
	MergedImage[0:480, 640:1280]=frame2
 
        cv2.imshow("Merged Images", MergedImage)
        #cv2.imshow("Cam1", frame1)
        #cv2.imshow("Cam2", frame2)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# When everything done, release the capture
cap1.release()
cap2.release()

cv2.destroyAllWindows()
