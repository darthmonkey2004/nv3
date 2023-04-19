from random import randint
import cv2
from new_object import new_object
from conf import *
opts = readConf()['cameras'][2]
cap = cv2.VideoCapture(0)



def draw_on_image(img, det):
	font = opts['FONT']
	font_scale = opts['FONT_SCALE']
	line_type = cv2.LINE_AA
	line_size = 2
	drawn = img.copy()
	color = (randint(0, 255), randint(0, 255), randint(0, 255))
	drawn = cv2.rectangle(img, (int(det.l), int(det.t)), (int(det.r), int(det.b)), color, 2)
	y = int(det.t) + 30
	coords = (int(det.l), int(y))
	drawn = cv2.putText(drawn, det.class_name, coords, font, font_scale, color, line_size, line_type)
	return drawn

def test_inner(det1, det2):
	if det1.area > det2.area:
		outer = det1
		inner = det2
	elif det2.area > det1.area:
		outer = det2
		inner = det1
	if inner.l >= outer.l and inner.r <= outer.r and inner.t >= outer.t and inner.b <= outer.b:
		outer.class_name = inner.class_name
		return True, outer
	else:
		return False, None


new = new_object(2, 'box').new
ret, img = cap.read()

box1=(68, 17, 248, 317)
box1_name='person'
det1 = new(camera_id=2, box=box1, class_name=box1_name)
box2=(120, 64, 184, 128)
box2_name='Matt McClellan'
det2 = new(camera_id=2, box=box2, class_name=box2_name)
is_inner, det = test_inner(det1, det2)
if is_inner:
	img = draw_on_image(img, det)
else:
	img = draw_on_image(img, det1)
	img = draw_on_image(img, det2)
while True:
	cv2.imshow('image', img)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		cv2.destroyAllWindows()
		break
cap.release()
	


