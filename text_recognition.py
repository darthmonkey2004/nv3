import imutils
import cv2
import threading
from mss import mss
from conf import *
import numpy

class screencap():
	def __init__(self, camera_id=3):
		self.camera_id = camera_id
		self.opts = read_opts(self.camera_id)
		self.src_types = self.opts['src']['types']
		self.src_type = self.opts['src']['type']
		if self.src_type == 'screen_grab':
			self.monitor = self.opts['src']['monitor']
		else:
			self.monitor = None
		self.monitor = self.opts['src']['monitor']
		self.sct = mss()
		self.monitors = self.sct.monitors
		self.img = None
		self.runloop = True
		self._start()

	def _capture(self):
		while self.runloop:
			try:
				img = numpy.asarray(self.sct.grab(self.monitor))
				#go through convoluted transform to remove 4th channel (look this up, should be reshape possibilities)
				self.img = cv2.cvtColor(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), cv2.COLOR_RGB2BGR)
			except Exception as e:
				self.img = None
				print(f"screencap.read():Exception! ({e})", 'error')
				break
		self.img = None
		return

	def _start(self):
		try:
			self.t = threading.Thread(target=self._capture)
			self.t.setDaemon(True)
			self.t.start()
			return True
		except Exception as e:
			print("Failed to start thread:", e)
			return False

	def read(self):
		img = self.img
		if img is None:
			return False, None
		else:
			return True, img

	def release(self):
		self.runloop = False


class readText():
	def __init__(self):
		self.net = cv2.dnn.readNet('/home/monkey/.local/lib/python3.8/site-packages/nv3/models/frozen_east_text_detection.pb')
		self.cap = screencap()
		self.runloop = True

	def loop(self):
		while self.runloop:
			ret, img = self.cap.read()
			if ret:
				img, boxes = self.detect(img)
				cv2.imshow('image', img)
				k = cv2.waitKey(1) & 0xff
				if k == 115:
					break
		self.cap.release()
		exit()
				

	def detect(self, img):
		imgWidth = 320
		imgHeight = 320
		orig = img.copy()
		(H, W) = img.shape[:2]
		(newW, newH) = (imgWidth, imgHeight)
		rW = W / float(newW)
		rH = H / float(newH)
		img = imutils.resize(img, width=320, height=320)
		(H, W) = img.shape[:2]
		blob = cv2.dnn.blobFromImage(img, 1.0, (W, H), (123.68, 116.78, 103.94), swapRB=True, crop=False)
		outputLayers = []
		outputLayers.append("feature_fusion/Conv_7/Sigmoid")
		outputLayers.append("feature_fusion/concat_3")
		self.net.setInput(blob)
		output = self.net.forward(outputLayers)
		self.scores = output[0]
		self.geometry = output[1]
		(numRows, numColf) = scores.shape[2:4]
		rects = []
		confidences = []
		for y in range(0, numRows):
			scoresData = scores[0, 0, y]
			xData0 = geometry[0, 0, y]
			xData1 = geometry[0, 1, y]
			xData2 = geometry[0, 2, y]
			xData3 = geometry[0, 3, y]
			anglesData = geometry[0, 4, y]
			
			for x in range(0, numCols):
				if scoresData[x] < 0.5:
					continue
				(offsetX, offsetY) = (x * 4.0, y * 4.0)
				angle = anglesData[x]
				cos = np.cos(angle)
				sin = np.sin(angle)
				h = xData0[x] + xData2[x]
				w = xData1[x] + xData3[x]
				endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
				endY = int(offSetY - (sin * xData1[x]) + (cos * xData2[x]))
				startX = int(endX - w)
				startY = int(endY - h)
				rects.append((startX, startY, endX, endY))
				confidences.append(scoresData[x])
		boxes = non_max_supression(np.array(rects), probs=confidences)
		for (startX, startY, endX, endY) in boxes:
			startX = int(startX * rW)
			startY = int(startY * rH)
			endX = int(endX * rW)
			endY = int(endY * rH)
			cv2.rectangle(orig, (startX, startY), (endX, endY), (randint(0, 255), randint(0, 255), randint(0, 255)), 2)
		return orig, boxes
			
