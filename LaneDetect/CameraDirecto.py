import numpy as np
import cv2

cap = cv2.VideoCapture(0)

cv2.namedWindow("Camera", cv2.WND_PROP_FULLSCREEN);
#cv2.namedWindow("Camera", 1);
cv2.setWindowProperty("Camera", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN);
#cv2.setWindowProperty("Camera", 1, 3);

while(True):
    # Capture frame-by-frame
 
    while (True):
        ret, frame = cap.read()

 
        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()



#cv2.ellipse(resized,(25,25),(100,50),0,0,180,255,-1)
    #ret,thresh = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
    #thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
    #        cv2.THRESH_BINARY,11,2)
