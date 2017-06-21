import numpy as np
import cv2
import track
import detect

cap = cv2.VideoCapture(1)

cv2.namedWindow("Camera", cv2.WND_PROP_FULLSCREEN);
#cv2.namedWindow("Camera", 1);
cv2.setWindowProperty("Camera", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN);
#cv2.setWindowProperty("Camera", 1, 3);

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    ticks = 0

    lt = track.LaneTracker(2, 0.1, 500)
    ld = detect.LaneDetector(180)
#   while cap.isOpened():
    while (True):
        precTick = ticks
        ticks = cv2.getTickCount()
        dt = (ticks - precTick) / cv2.getTickFrequency()

        ret, frame = cap.read()

        predicted = lt.predict(dt)

        lanes = ld.detect(frame)

        if predicted is not None:
            cv2.line(frame, (predicted[0][0], predicted[0][1]), (predicted[0][2], predicted[0][3]), (0, 0, 255), 5)
            cv2.line(frame, (predicted[1][0], predicted[1][1]), (predicted[1][2], predicted[1][3]), (0, 0, 255), 5)

        lt.update(lanes)


#        r = 320.0 / frame.shape[1]
#        dim = (320, int(frame.shape[0] * r))
#        resized = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)

        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

#    cv2.imshow("Camera",resized)
#    if cv2.waitKey(1) & 0xFF == ord('q'):
#        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()



#cv2.ellipse(resized,(25,25),(100,50),0,0,180,255,-1)
    #ret,thresh = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
    #thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
    #        cv2.THRESH_BINARY,11,2)
