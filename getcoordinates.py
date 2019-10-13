import cv2
import numpy as np

# mouse callback function
def getcordinates(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        print(x,y)

# Insert the image you want
img = cv2.imread('new2.jpg',1)
cv2.namedWindow('image')
cv2.setMouseCallback('image',getcordinates)

while(1):
    cv2.imshow('image',img)
    if cv2.waitKey(20) & 0xFF == 27:
        break
cv2.destroyAllWindows()