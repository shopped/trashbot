import cv2

#cam = cv2.VideoCapture(0)
cam = cv2.VideoCapture(1)

ret, frame = cam.read()

img_name = "test.jpg"

cv2.imwrite(img_name, frame)

cam.release()


