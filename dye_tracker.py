#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 23 18:01:48 2020

@author: espeon
"""

#import os
import cv2
import numpy as np
import sys


print("Python version: \n" + sys.version)
print("cv2 version: " + cv2.__version__)

#set range of HSV values
lowerBound = np.array([63, 20, 165])
upperBound = np.array([109, 255, 255])

#upload video file
cam = cv2.VideoCapture("/Users/espeon/spyder3-py3/joined-out-stab.mp4")
kernelOpen = np.ones((5, 5))
kernelClose = np.ones((20, 20))

# initialize lists
areas_list = []
contours_list = []
dye_pix = []

while(cam.isOpened()):
    ret, original = cam.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    # resize image
    original = cv2.resize(original, (680,440))
    # invert image since reds wrap around
    img = (255-original)
    # convert BGR to HSV and blur w.r.t. edges
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    blur = cv2.bilateralFilter(imgHSV,10,300,300)

    mask = cv2.inRange(blur, lowerBound, upperBound)
    maskOpen = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernelOpen)
    maskClose = cv2.morphologyEx(maskOpen, cv2.MORPH_CLOSE, kernelClose)
    maskFinal = maskClose
    
    # ROI
    black = np.zeros((img.shape[0], img.shape[1], 3), np.uint8) #---black in RGB
    black1 = cv2.rectangle(black,(200,70),(500,350),(255, 255, 255), -1) #-----ROI
    gray = cv2.cvtColor(black,cv2.COLOR_BGR2GRAY)
    ret,b_mask = cv2.threshold(gray,127,255, 0) #----converted to binary

    fin = cv2.bitwise_and(b_mask,b_mask,mask = mask) #-----ROI mask
    
    contours =  cv2.findContours(fin,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
    
    # loop over the contours
    for c in contours:
        area = cv2.contourArea(c)
        if area>150: # ignore anomalies
            cv2.drawContours(original, [c], -1, (0,255,0), 3)
    
            # compute the center of the contour        
            M = cv2.moments(c)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            
            # plot centroid onto object
            #cv2.circle(original, (cx, cy), 3, (255, 255, 255), -1)
            
            areas_list.append(area)
            contours_list.append(c)
            dye_pix.append(cv2.countNonZero(fin))
    

    cv2.imshow("Mask", fin)
    cv2.imshow("Spill with contours",original)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
cam.release()

# convert lists to arrays
areas_array = np.array(areas_list)
contours_array = np.array(contours_list)
dye_pix_array = np.array(dye_pix)
total_pix = 440*680
pix_density = dye_pix_array/total_pix 

cv2.destroyAllWindows()