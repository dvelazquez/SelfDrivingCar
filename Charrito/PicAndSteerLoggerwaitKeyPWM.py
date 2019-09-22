"""
   This program takes a picture and labels it with the steering wheel angle
   and makes a CSV log for post CNN training in Colab to compile the .h5 file
   to predict future pictures-> angles 
   
   Daniel Velazquez
   July 2019 - with SPI
   Sep 2019 - Added direct PWM control from Raspi
"""

import RPi.GPIO as IO          #calling header file which helps us use GPIOs of PI
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import cv2
import time
from time import strftime
import datetime

import csv

Log_filename = strftime("%Y-%m-%d %H:%M:%S")

PicNumber=0
camera=PiCamera()
rawCapture = PiRGBArray(camera)

cv2.namedWindow('Need this for waitKey', 1)

# Initial PWM
IO.setwarnings(False)           #do not show any warnings
IO.setmode (IO.BCM)         #we are programming the GPIO by BCM pin numbers. (PIN35 as GPIO19)
IO.setup(14,IO.OUT)           # initialize GPIO19 as an output.
IO.setup(15,IO.OUT)           # initialize GPIO19 as an output.

Direction = IO.PWM(14,200)       #GPIO15 as PWM output for direction, with YY Hz frequency
Traction = IO.PWM(15,1)          #GPIO14 as PWM output for traction, with XX Hz frequency


Traction.start(100)                              #generate PWM signal with 0% duty cycle
Direction.start(50)                              #generate PWM signal with 0% duty cycle

x=74

#cv2.waitKey(100)

with open('%s.csv' %Log_filename, "a") as log:
	while(True):	    # Capture picture and label the angle
		rawCapture = PiRGBArray(camera)
		camera.capture(rawCapture, format="bgr")
		frame=rawCapture.array
		PicNumber += 1
		cv2.imwrite('log/CharritoPic_%s.jpg' %PicNumber, frame)
		
		c= 0
		c= cv2.waitKey(1)	

		if c == 97:
			x = x + 2

		if c == 115:
			x = x - 2
		
		if x >= 82:		# Limit max right to RR
			x = 82
		if x <= 66:		# Limit max left to LL
			x = 66
		if c == 113:
			break

		Direction.ChangeDutyCycle(x)

		print "                               Wheel direction", x
		log.write("{0},{1}\n".format(str('CharritoPic_%s.jpg' %PicNumber), str(x/100.0)))
   

# When everything done, release the capture
Traction.ChangeDutyCycle(0)
camera.release()
cv2.destroyAllWindows()
