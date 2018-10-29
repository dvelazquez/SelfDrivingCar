# Ejercicio 01 - Camera Input
# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html
# Daniel Velazquez Oct 18

import numpy as np
import cv2

cap = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

	# Aqui vamos a hacer el procesamiento

    # Display the resulting frame
    cv2.imshow('Camara',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
