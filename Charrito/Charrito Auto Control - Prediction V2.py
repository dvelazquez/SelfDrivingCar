"""
	Predict steering angle using model.h5 compiled using colab
	running with Python off line, for El Charrito
	
	Daniel Velazquez - Septiembre 2019
"""
import numpy as np
from keras.models import load_model
import matplotlib.image as mpimg
from PIL import Image
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import RPi.GPIO as IO          #calling header file which helps us use GPIOs of PI

import time
from time import strftime
import datetime
import csv

Log_filename = strftime("%Y-%m-%d %H:%M:%S")

PicNumber=0

model = load_model('CharritoModel_K2.2.5.h5')
camera=PiCamera()

cv2.namedWindow('Need this for waitKey', 1)

# Initialize PWM
IO.setwarnings(False)           #do not show any warnings
IO.setmode (IO.BCM)         #we are programming the GPIO by BCM pin numbers. (PIN35 as GPIO19)
IO.setup(14,IO.OUT)           # initialize GPIO19 as an output.
IO.setup(15,IO.OUT)           # initialize GPIO19 as an output.

Direction = IO.PWM(14,200)       #GPIO15 as PWM output for direction, with YY Hz frequency
Traction = IO.PWM(15,1)          #GPIO14 as PWM output for traction, with XX Hz frequency

Traction.start(80)                              #generate PWM signal with 0% duty cycle
Direction.start(50)                              #generate PWM signal with 0% duty cycle

x=73



def img_preprocess(img):
  img = img[100:450,:,:]    # This is the area that has the road, will change with camera position
  img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
  img = cv2.GaussianBlur(img, (3,3),0)
  img= cv2.resize(img, (200,66))
  img = img/255
  return img


with open('%s.csv' %Log_filename, "a") as log:
	while(True):
		print("While Cycle")   # for debugging
		rawCapture = PiRGBArray(camera)
		camera.capture(rawCapture, format="bgr")
		image=rawCapture.array


		# This part is to manually steer the car in case prediction takes it badly
		PicNumber += 1
		cv2.imwrite('log/CharritoAuto_Pic_%s.jpg' %PicNumber, image)
		c= 0
		c= cv2.waitKey(1)

		if c == 97:
			x = x + 2
			Direction.ChangeDutyCycle(x)
		if c == 115:
			x = x - 2
			Direction.ChangeDutyCycle(x)
		if x >= 82:		# Limit max right to RR
			x = 82
		if x <= 66:		# Limit max left to LL
			x = 66
		if c == 113:
			break


		image= img_preprocess(image)
		print("Image PreProcessed")

		#cv2.imshow("Window",image)
		#k = cv2.waitKey(0) #  Need to loop this 
		image= np.array([image])
		SteeringPrediction = float(model.predict(image))
		print('Predicted Steer Position: ',SteeringPrediction)


		# Convert prediction to PWM %
		x= ((SteeringPrediction*7)+73)
		Direction.ChangeDutyCycle(x)
		print('Predicted PWM Steer Position: ',x)

		log.write("{0},{1}\n".format(str('CharritoAuto_Pic_%s.jpg' %PicNumber), str(x)))

