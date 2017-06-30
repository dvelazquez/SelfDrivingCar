# import the necessary packages
import time
import cv2
import numpy as np

#Difference Variable
minDiff = 10000
minSquareArea = 5000
match = -1

#Frame width & Height
w=640
h=480

#Reference Images Display name & Original Name
#ReferenceImages = ["ArrowL.jpg","ArrowR.jpg","ArrowT.jpg","Ball.jpg","Go.jpg","Stop.jpg90","Turn Around","Search for Ball","Start..","Stop!"]
ReferenceImages = ["ArrowL.jpg","ArrowR.jpg","Stop.jpg"]
ReferenceTitles = ["Left","Right","Stop"]

#define class for References Images
class Symbol:
    def __init__(self):
        self.img = 0
        self.name = 0

#define class instances (6 objects for 6 different images)
symbol= [Symbol() for i in range(3)]



def readRefImages():
    for count in range(3):    #Here 2 is the number of images to count
        image = cv2.imread(ReferenceImages[count], cv2.COLOR_BGR2GRAY)
        symbol[count].img = cv2.resize(image,(w/2,h/2),interpolation = cv2.INTER_AREA)
        symbol[count].name = ReferenceTitles[count]
        #cv2.imshow(symbol[count].name,symbol[count].img);


def order_points(pts):
        # initialzie a list of coordinates that will be ordered
        # such that the first entry in the list is the top-left,
        # the second entry is the top-right, the third is the
        # bottom-right, and the fourth is the bottom-left
        rect = np.zeros((4, 2), dtype = "float32")

        # the top-left point will have the smallest sum, whereas
        # the bottom-right point will have the largest sum
        s = pts.sum(axis = 1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        # now, compute the difference between the points, the
        # top-right point will have the smallest difference,
        # whereas the bottom-left will have the largest difference
        diff = np.diff(pts, axis = 1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        # return the ordered coordinates
        return rect

def four_point_transform(image, pts):
        # obtain a consistent order of the points and unpack them
        # individually
        rect = order_points(pts)
        (tl, tr, br, bl) = rect

        maxWidth = w/2
        maxHeight = h/2

        dst = np.array([
                [0, 0],
                [maxWidth - 1, 0],
                [maxWidth - 1, maxHeight - 1],
                [0, maxHeight - 1]], dtype = "float32")

        # compute the perspective transform matrix and then apply it
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

        # return the warped image
        return warped


def auto_canny(image, sigma=0.33):
        # compute the median of the single channel pixel intensities
        v = np.median(image)

        # apply automatic Canny edge detection using the computed median
        lower = int(max(0, (1.0 - sigma) * v))
        upper = int(min(255, (1.0 + sigma) * v))
        edged = cv2.Canny(image, lower, upper)

        # return the edged image
        return edged


def resize_and_threshold_warped(image):
        #Resize the corrected image to proper size & convert it to grayscale
        #warped_new =  cv2.resize(image,(w/2, h/2))
        warped_new_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        #Smoothing Out Image
        blur = cv2.GaussianBlur(warped_new_gray,(5,5),0)

        #Calculate the maximum pixel and minimum pixel value & compute threshold
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(blur)
        threshold = (min_val + max_val)/2

        #Threshold the image
        ret, warped_processed = cv2.threshold(warped_new_gray, threshold, 255, cv2.THRESH_BINARY)

        #return the thresholded image
        return warped_processed




def main():

    #Font Type
    font = cv2.FONT_HERSHEY_SIMPLEX


    # initialize the camera and grab a reference to the raw camera capture
    video = cv2.VideoCapture(1)

    #Windows to display frames
    cv2.namedWindow("Main Frame", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("Matching Operation", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("Corrected Perspective", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("Contours", cv2.WINDOW_AUTOSIZE)

    #Read all the reference images
    readRefImages()

    # capture frames from the camera
    while True:
            ret, OriginalFrame = video.read()
            gray = cv2.cvtColor(OriginalFrame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray,(3,3),0)

            #Detecting Edges
            edges = auto_canny(blurred)

            #Contour Detection & checking for squares based on the square area
            cntr_frame, contours, hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                    approx = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)

                    if len(approx)==4:
                            area = cv2.contourArea(approx)

                            if area > minSquareArea:
                                    cv2.drawContours(OriginalFrame,[approx],0,(0,0,255),2)
                                    warped = four_point_transform(OriginalFrame, approx.reshape(4, 2))
                                    warped_eq = resize_and_threshold_warped(warped)

                                    for i in range(3):  #also range here is the number of images
                                        diffImg = cv2.bitwise_xor(warped_eq, symbol[i].img)
                                        diff = cv2.countNonZero(diffImg);

                                        if diff < minDiff:
                                            match = i

                                            print symbol[i].name, diff
                                            print approx.reshape(4,2)[0]
                                            cv2.putText(OriginalFrame,symbol[i].name, (10,30), font, 1, (255,0,255), 2, cv2.LINE_AA)
                                            cv2.putText(OriginalFrame,symbol[i].name, tuple(approx.reshape(4,2)[0]), font, 1, (255,0,255), 2, cv2.LINE_AA)
                                            diff = minDiff
                                            break;

                                    cv2.imshow("Corrected Perspective", warped_eq)
                                    cv2.imshow("Matching Operation", diffImg)
                                    cv2.imshow("Contours", edges)

            #Display Main Frame
            cv2.imshow("Main Frame", OriginalFrame)

            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                    break

    video.release()
    cv2.destroyAllWindows()


#Run Main
if __name__ == "__main__" :
    main()

