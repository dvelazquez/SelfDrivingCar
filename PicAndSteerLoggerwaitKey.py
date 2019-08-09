"""
   This program takes a picture and labels it with the steering wheel angle
   and makes a CSV log for post CNN training in Colab to compile the .h5 file
   to predict future pictures-> angles 
   
   Daniel Velazquez
   July 2019
   
   --- SPI Controller based on:
   Arturo Reta - Omar Cumplido    Octubre 2018      master_spi2.py
"""

from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import cv2
# SPI
import time
from time import strftime
import spidev
import datetime

import csv

Log_filename = strftime("%Y-%m-%d %H:%M:%S")

PicNumber=0
camera=PiCamera()
rawCapture = PiRGBArray(camera)

cv2.namedWindow('Need this for waitKey', 1)


# We only have SPI bus 0 available to us on the Pi
bus = 0
#Device is the chip select pin. Set to 0 or 1, depending on the connections
device = 1
# Enable SPI
spi = spidev.SpiDev()
# Open a connection to a specific bus and device (chip select pin)
spi.open(bus, device)
# Set SPI speed and mode
spi.max_speed_hz = 200000
spi.mode = 0

# Initial SPI
msg0=01
msg1=140   # Start centered
spi.xfer2([msg0] + [msg1])  # Left 100 - Center 140 - Right 180
result = spi.xfer2([msg0])
result = spi.xfer2([msg1])

cv2.waitKey(100)
#msg0= 02
#msg1= 80
spi.xfer2([02] + [80])		# is PWM 80 slowest?
result = spi.xfer2([msg0])
result = spi.xfer2([msg1])
msg0=01
msg1=140

with open('%s.csv' %Log_filename, "a") as log:
	while(True):	    # Capture picture and label the angle
		rawCapture = PiRGBArray(camera)
		camera.capture(rawCapture, format="bgr")
		frame=rawCapture.array
		PicNumber += 1
		cv2.imwrite('log/CharritoPic_%s.jpg' %PicNumber, frame)
		
		c= 0
		
		#if cv2.waitKey(1) & 0xFF == ord('q'):
		#c=raw_input('Left=A, Right=S: ' )
		c= cv2.waitKey(1)
		#if 's' == chr(c & 255):
		#if c.upper() == 'S':
		if c == 97:
			msg1 = msg1 + 10
		#if cv2.waitKey(1) & 0xFF == ord('a'):
		#if 'a' == chr(c & 255):
		#if c.upper() == 'A':
		if c == 115:
			msg1 = msg1 - 10	
		if msg1 >= 180:		# Limit max right to 180
			msg1 = 180
		if msg1 <= 100:		# Limit max left to 100
			msg1 = 100
		if c == 113:
			spi.xfer2([02] + [150])		# STOP
			result = spi.xfer2([msg0])
			result = spi.xfer2([msg1])
			break
		spi.xfer2([msg0] + [msg1])
		result = spi.xfer2([msg0])
		result = spi.xfer2([msg1])
		result= (140.0-float(msg1))/40.0
		print "                               Wheel direction", result
		log.write("{0},{1}\n".format(str('CharritoPic_%s.jpg' %PicNumber), str(result)))
   

# When everything done, release the capture
camera.release()
cv2.destroyAllWindows()
