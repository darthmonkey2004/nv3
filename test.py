from tt import *
from analyze_bak import *
from capture_new import *
a = analyze(camera_id=3)
cap = capture(3)
is_tracking = False


def draw_on_image(img, boxes):
	w = img.shape[1]
	h = img.shape[0]
	drawn = img.copy()
	for box in boxes:
		print(box.class_name, box.box)
		if isinstance(box, (tracker,nvbox)):
			class_name = box.class_name
			drawn = cv2.rectangle(img, (int(box.l), int(box.t)), (int(box.r), int(box.b)), box.color, 2)
			y = box.t + 30
			coords = (int(box.l), int(y))
			drawn = cv2.putText(drawn, box.class_name, coords, box.font, box.font_scale, box.color, box.line_size, box.line_type)
			#drawn = cv2.putText(drawn, object_name, coords, opts['FONT'], opts['FONT_SCALE'], BLUE, 2, cv2.LINE_AA)
		else:
			class_name = 'Motion detected!'
			drawn = cv2.rectangle(img, (int(box[0]), int(box[1]), int(box[2]), int(box[3])), (randint(0, 255), randint(0, 255), randint(0, 255)), 2)
			y = int(box[1]) + 30
			coords = (int(box[0]), int(y))
			drawn = cv2.putText(drawn, object_name, coords, opts['FONT'], opts['FONT_SCALE'], box.color, box.line_size, box.line_type)
		
	return drawn

cv2.namedWindow('image', cv2.WINDOW_NORMAL)
cv2.resizeWindow('image', (1024, 768))
while True:
	ret, img = cap.read()
	if not ret:
		pass
	else:
		if not is_tracking:
			ret, dets = a.get_detection()
			if ret:
				img = draw_on_image(img, dets)
				print(dets[0].class_name, dets[0].box)
				t = tracker(img=img, det=dets[0])
				is_tracking = t.success
				print("istracking:", is_tracking)
		else:
			is_tracking = t.update(img)
			if is_tracking:
				img = draw_on_image(img, [t])
	cv2.imshow('image', img)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		cap.release()
		break
				
