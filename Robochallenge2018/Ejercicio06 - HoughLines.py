# Ejercicio 06 - Hough Lines
# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html
# Daniel Velazquez Oct 18

import numpy as np
import cv2
#from matplotlib import pyplot as plt

cap = cv2.VideoCapture(0)

 
while (True):
	ret, frame = cap.read()
	# COLOR SPACE
	frame=cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

	#RED EXTRACT
	lower_red = np.array([0,50,50]) 	#example value
	upper_red = np.array([10,255,255]) 	#example value
	mask = cv2.inRange(frame, lower_red, upper_red)
	img_result = cv2.bitwise_and(frame, frame, mask=mask)

	img_result=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	# THRESHOLDING
	retval, img_result = cv2.threshold(img_result,120,255,cv2.THRESH_BINARY)

	# FILTERING
	median = cv2.medianBlur(img_result,5)	# esta tiene dos lineas blancas con madres
	
	# FIND LINES
	rho = 100  # distance resolution in pixels of the Hough grid
	theta = np.pi / 180  # angular resolution in radians of the Hough grid
	threshold = 100  # minimum number of votes (intersections in Hough grid cell)
	min_line_length = 200  # minimum number of pixels making up a line
	max_line_gap = 50  # maximum gap in pixels between connectable line segments
	line_image = np.copy(median) * 0
	lines = cv2.HoughLinesP(median, rho, theta, threshold, np.array([]),min_line_length, max_line_gap)
	for line in lines:
		for x1,y1,x2,y2 in line:
			cv2.line(line_image,(x1,y1),(x2,y2),(255,0,255),5)
	print(len(lines),lines)
	lines_edges = cv2.addWeighted(median, 0.8, line_image, 1, 0)
	
	
	cv2.imshow("Camera", line_image)
	#raw_input("Press Enter to continue ...")

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
