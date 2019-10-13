import cv2

def Reverse(lst):
    return [ele for ele in reversed(lst)]

#provide the path for image of text box identification has to be done
image = cv2.imread('user1.jpg')
width = int(image.shape[1] )
height = int(image.shape[0])
# print(width,height)

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5,5), 0)
thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,11,30)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9,9))
dilate = cv2.dilate(thresh, kernel, iterations=4)

cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]

ROI_number = 0
points = []
for c in cnts:
    area = cv2.contourArea(c)
    if area > 2000 and area<70000 :
        x,y,w,h = cv2.boundingRect(c)
        cv2.rectangle(image, (x, y), (x + w, y + h), (12,255,32), 3)
        point = [x,y,x+w,y+h]
        points.append(point)
        ROI = image[y:y+h, x:x+w]
        cv2.imwrite('ROI_'+str(ROI_number)+'.jpg', ROI)
        ROI_number += 1

points=Reverse(points)
print(points)
gap =[]
l=len(points)

for p in range(l-1):
    dist = points[p+1][1]-points[p][3]
    gap.append(dist)
# print(gap)

for p in range(l-1):
    dist = points[p+1][2] - points[p][0]
    print(dist)

cv2.imshow('blur', blur)
cv2.imshow('thresh', thresh)
cv2.imshow('dilate', dilate)
cv2.imshow('image', image)
cv2.waitKey()
