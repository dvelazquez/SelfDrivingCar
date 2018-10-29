# Ejercicio 04 - Red Extract y Binarizar
# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html
# Daniel Velazquez Oct 18


import numpy as np
import cv2

cap = cv2.VideoCapture(0)

#cv2.namedWindow("Camera", cv2.WND_PROP_FULLSCREEN);
#cv2.namedWindow("Camera", 1);
#cv2.setWindowProperty("Camera", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN);
#cv2.setWindowProperty("Camera", 1, 3);
 
while (True):
	ret, frame = cap.read()
	frame=cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

	lower_red = np.array([0,50,50]) 	#example value
	upper_red = np.array([10,255,255]) 	#example value
	mask = cv2.inRange(frame, lower_red, upper_red)
	img_result = cv2.bitwise_and(frame, frame, mask=mask)

	img_result=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	# THRESHOLDING
	retval, img_result = cv2.threshold(img_result,120,255,cv2.THRESH_BINARY)

	cv2.imshow("Camera", img_result)

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
