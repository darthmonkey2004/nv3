from detector import detector
import cv2
from tracker import *

def draw_on_image(img, boxes):
	w = img.shape[1]
	h = img.shape[0]
	drawn = img.copy()
	for box in boxes:
		drawn = cv2.rectangle(img, (int(box.l), int(box.t)), (int(box.r), int(box.b)), box.color, box.line_size)
		y = box.t + 30
		coords = (int(box.l), int(y))
		drawn = cv2.putText(drawn, box.class_name, coords, box.font, box.font_scale, box.color, box.line_size, box.line_type)
	return drawn


d = detector(0)
cap = cv2.VideoCapture(0)
tracking = False
t = None
skip_frames = 15
pos = 0
opts = read_opts(0)
tracker_type = opts['tracker']['types']['selected']
types = opts['tracker']['types']['available']
while True:
	ret, img = cap.read()
	if ret:
		pos += 1
		if not tracking and pos == 15:
			pos = 0
			dets = d.detect(img)
			if dets != []:
				#print(dets)
				img = draw_on_image(img, dets)
				t = tracker(img=img, box=dets[0].box, camera_id=0, class_name=dets[0].class_name, tracker_type=tracker_type, confidence=dets[0].confidence)
				tracking = t.success
				if tracking:
					#print(dir(t))
					print(f"t.class_name:{t.class_name}, t.age:{t.age}, t.box:{t.box}")
		elif tracking:
			pos = 0
			ret = t.update(img)
			if ret:
				tracking = True
				img = draw_on_image(img, [t])
				#print(f"t.class_name:{t.class_name}, t.age:{t.age}, t.box:{t.box}, t.misses:{t.misses}")
			else:
				tracking = False
		cv2.imshow('image', img)
		k = cv2.waitKey(1) & 0xff
		if k == 113:
			break
		elif k == 116:
			pos = -1
			for _type in types:
				pos += 1
				print(f"{pos}. {_type}")
			idx = int(input("Enter number of new tracker type: "))
			tracker_type = types[idx]
			print(f"Switched to type: {tracker_type}!")
		elif k == 114:
			tracking = False
			print("reset tracker!")
		else:
			if k != 255:
				print(k)
cap.release()
exit()
			


