import pickle
import cv2
from detector import detector

d = detector(0)

while True:
	with open('img.dat', 'rb') as f:
		img = pickle.load(f)
		f.close()
	dets = d.detect(img)
	for det in dets:
		print("dets:", dets)
		print(det.box, det.class_name, det.tolerance, det.confidence, det.pid, det.distance, det.type)
