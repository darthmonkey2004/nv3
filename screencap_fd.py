from imutils import resize
import cv2
from capture import *
detector = cv2.CascadeClassifier('/home/monkey/.np/nv/haarcascade_frontalface_default.xml')
cap = capture(0)

def draw_on_image(img, boxes):
	w = img.shape[1]
	h = img.shape[0]
	drawn = img.copy()
	for x, y, w, h in boxes:
		l, t = x, y
		r = x + w
		b = y + h
		print(l, t, r, b)
		object_name = 'Face'
		drawn = cv2.rectangle(img, (int(l), int(t)), (int(r), int(b)), (0, 0, 255), 2)
		y = t + 30
		coords = (int(l), int(y))
		drawn = cv2.putText(drawn, object_name, coords, 0, 1, (0, 255, 0), 2, cv2.LINE_AA)
	return drawn


def kill():
	cv2.destroyAllWindows()

skip = 20
ct = 0
cv2.namedWindow('image', cv2.WINDOW_NORMAL)
while True:
	ct += 1
	ret, img = cap.read()
	if ret:
		#gray = cv2.cvtColor(resize(img, width=640), cv2.COLOR_BGR2GRAY)
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		#faces = detector.detectMultiScale(gray, scaleFactor=2.0, minNeighbors=5, minSize=(15, 15))
		if ct == skip:
			ct = 0
			faces = detector.detectMultiScale(gray, scaleFactor=3.0, minNeighbors=5, minSize=(20, 20))
			if len(faces) > 0:
				img = draw_on_image(img, faces)
		cv2.imshow('image', img)
		k = cv2.waitKey(1) & 0xff
		if k == 113:
			break

kill()
