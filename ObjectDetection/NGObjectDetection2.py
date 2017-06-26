import cv2
import urllib
import time
import numpy as np
from LoadSymbols import Symbol

from websocket import create_connection

# Width & Height From Camera
width = 640
height = 480

# Difference Variables
minDiff = 8000
minSquareArea = 2000
match = -1

# Middle X
MidX = width/2
MidY = height/2

# Font Type
font = cv2.FONT_HERSHEY_SIMPLEX

# Needed Variables for holding points for perspective correction
rect = np.zeros((4, 2), dtype = "float32")
maxW = width/2
maxH = height/2
dst = np.array([
        [0, 0],
        [maxW - 1, 0],
        [maxW - 1, maxH - 1],
        [0, maxH - 1]], dtype = "float32")

# Instance for Streaming
stream = urllib.urlopen('http://192.168.137.188:8080/?action=stream')
webSocket = create_connection("ws://192.168.137.188:8000")

# Reference Images Display name & Original Name
Reference_Symbols = ["Symbols/ArrowL.jpg",
                     "Symbols/ArrowR.jpg",
                     "Symbols/ArrowT.jpg",
                     "Symbols/Ball.jpg",
                     "Symbols/Go.jpg",
                     "Symbols/Stop.jpg"]
Symbol_Titles = ["Turn Left 90",
                 "Turn Right 90",
                 "Turn Around",
                 "Search for Ball",
                 "Start..",
                 "Stop!"]
Actions = ["Left", "Right", "Back", "Ball", "Go", "Stop"]

# Define Class Instances for Loading Reference Images (6 objects for 6 different images/symbols)
symbol= [Symbol() for i in range(6)]

def load_symbols():
    for count in range(6):
        symbol[count].read(Reference_Symbols[count], Symbol_Titles[count], size=(width/2, height/2))
        print "Loading: ", symbol[count].name
    print "All Reference Images Are Successfully Loaded!"

def arduino_string(arduinoList=[], *args):
    return ''.join(['A1:', str(arduinoList[0]), '&2:', str(arduinoList[1])])

def servo_string(servoAngle):
    servoDC = 5./180.*(servoAngle)+5
    return ''.join(['S', str(round(servoDC, 2))])

def generate_windows():
    # Windows to display frames
    cv2.namedWindow("Main Frame", cv2.WINDOW_AUTOSIZE)
    # cv2.namedWindow("Matching Operation", cv2.WINDOW_AUTOSIZE)
    # cv2.namedWindow("Corrected Perspective", cv2.WINDOW_AUTOSIZE)

def get_canny_edge(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)

    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)

    # return the edged image
    return edged

def correct_perspective(frame, pts):
    # Sort the contour points in Top Left, Top Right, Bottom Left & Bottom Right Manner
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # Compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(frame, M, (width/2,height/2))
    warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)

    # Calculate the maximum pixel and minimum pixel value & compute threshold
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(warped)
    threshold = (min_val + max_val)/2
    
    # Threshold the image
    ret, warped = cv2.threshold(warped, threshold, 255, cv2.THRESH_BINARY)

    # Return the warped image
    return warped

def main():
    load_symbols()
    generate_windows()
    bytes = ''
    match = -1
    w_save = 0
    motor_speed = 150
    displayText = []
    turn = False
    sign_found = False

    while True:
        bytes += stream.read(2048)
        
        a = bytes.find('\xff\xd8')
        b = bytes.find('\xff\xd9')

        if a!=-1 and b!=-1:
            jpg = bytes[a:b+2]
            bytes = bytes[b+2:]
            camera_frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)

            # camera_frame = cv2.flip(camera_frame, 0)
            # camera_frame = cv2.flip(camera_frame, 1)
    
            # Changing color-space to grayscale & Blurring the frames to reduce the noise
            gray = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray,(3,3),0)

            # Detecting Edges
            edges = get_canny_edge(blurred)

            # Contour Detection & checking for squares based on the square area
            cnt_frame, contours, hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

            # Sorting contours; Taking the largest, neglecting others
            contours = sorted(contours, key=cv2.contourArea, reverse=True) [:1]

            for cnt in contours:
                approx = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)

                if len(approx) == 4:
                    area = cv2.contourArea(approx)
                    
                    if area > minSquareArea:
                        warped = correct_perspective(camera_frame, approx.reshape(4, 2))

                        for i in range(6):
                                diffImg = cv2.bitwise_xor(warped, symbol[i].img)
                                diff = cv2.countNonZero(diffImg)

                                if diff < minDiff:
                                    match = i
                                    #diff = minDiff
                                    cnt = approx.reshape(4,2)
                                    displayText = tuple(cnt[0])
                                    sign_found = True
                                    break
            if sign_found == True:

                sign_found = False
                x,y,w,h = cv2.boundingRect(cnt)
                centroid_x = x + (w/2)
                centroid_y = y + (h/2)
                # Real width * focal length = 16175.288
                camera_range = round((16175.288 / w),0)
                # Draw the contours around sign & bounding box around sign & put the sign title
                cv2.drawContours(camera_frame, [cnt], 0, (255, 0, 0), 2)
                cv2.rectangle(camera_frame, (x, y), (x + w, y + h), (0, 255,0), 2)
                cv2.putText(camera_frame, symbol[match].name, displayText,font, 1, (255,0,255), 2, cv2.LINE_AA)

                if w < 420:
                    if camera_range == 0 or camera_range >= 60:
                        speed_adjust = 1.0 *(((centroid_x - 320) / 380.) * 80)
                        speed_adjust = round (speed_adjust)
                        motor_l = motor_speed + speed_adjust
                        motor_r = motor_speed - speed_adjust
                        webSocket.send(arduino_string([motor_l, motor_r]))
                        turn = False
                    else:
                        if w*h >= 70000 and turn == False:
                            if Actions[match] == "Back":
                                webSocket.send(arduino_string([230,230]))
#Back
                                match = -1
                                print "Turn Back"
                                turn = True
                            elif Actions[match] == "Left":
                                webSocket.send(arduino_string([235,235]))
#Left
                                match = -1
                                print "Left Turn"
                                turn = True
                            elif Actions[match] == "Right":
                                webSocket.send(arduino_string([232,232]))
#Right
                                match = -1
                                print "Right Turn"
                                turn = True
                            elif Actions[match] == "Stop":
                                webSocket.send(arduino_string([237,237]))
#Stop
                                match = -1
                                print "Stop"
                                turn = True
                                exit(0)
            else:
                centroid_x = 0
                centroid_y = 0
                camera_range = 0
                motor_r = 0
                motor_l = 0
                webSocket.send(arduino_string([motor_l, motor_r]))

        # Displaying co-ordinates & camera range
        central = 'Centre: X:%d : Y:%d ' % (centroid_x, centroid_y)
        distance = 'Range: %d cm' % (camera_range)
        cv2.putText(camera_frame, central,(20, 25), font, 0.65, (255,255,255), 1, cv2.LINE_AA)
        cv2.putText(camera_frame, distance,(20, 45), font, 0.65, (255,255,255), 1 , cv2.LINE_AA)
        
        # Displaying Frames
        cv2.imshow('Main Frame', camera_frame)

        if cv2.waitKey(1) == 27:
            break

        webSocket.close()
        stream.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
