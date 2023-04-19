from capture import *
from imgshow import *
import cv2
from conf import *
from new_object import new_object, message, nvbox
cap = screencap(0, width=1024, height=768)
d = display(0)
camera_id = 0
opts = read_opts(camera_id)
nvbox = new_object(camera_id=camera_id, object_name='box').new
cv2_recognizer = cv2.face.LBPHFaceRecognizer_create()
faceCascade = cv2.CascadeClassifier('/var/dev/nv3/models/haarcascade_frontalface_default.xml');
	
def fd(img, flip_image=False):
	if flip_image == True:
		img = cv2.flip(img, -1)
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	faces = faceCascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(20, 20))
	out = []
	for (x,y,w,h) in faces:
		box = (x, y ,x+w, y+h)
		name = 'Unrecognized Face'
		confidence = None
		det = nvbox(class_name=name, box=box, img=img, confidence=confidence)
		out.append(det)
	return out

def draw_on_image(img, boxes):
		w = img.shape[1]
		h = img.shape[0]
		drawn = img.copy()
		for box in boxes:
			object_name = 'Motion detected!'
			drawn = cv2.rectangle(img, (int(box.l), int(box.t)), (int(box.r), int(box.b)), box.color, 2)
			y = box.t + 30
			coords = (int(box.l), int(y))                                                                               
			print(box.box)
			drawn = cv2.putText(drawn, object_name, coords, opts['FONT'], opts['FONT_SCALE'], BLUE, 2, cv2.LINE_AA)
		return drawn

while True:
	ret, img = cap.read()
	if ret:
		out = fd(img)
		img = draw_on_image(img, out)
		d.show(img)
		if not d.is_open:
			break
