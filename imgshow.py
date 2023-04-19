import imutils
from nv_ui import *
import numpy as np
import os
import cv2
from conf import *
from utils import *
from log import nv_logger
from motion import bs_detector
from capture import capture, screencap
log = nv_logger().log_msg
import threading
import time

class display():
	def __init__(self, camera_id, width=1024, height=768):
		self.name = f"Camera: {camera_id}"
		conf = readConf()
		self.camera_id = camera_id
		self.opts = conf['cameras'][self.camera_id]
		self.fps = 30
		self.w = width
		self.h = height
		cv2.namedWindow(self.name, cv2.WINDOW_NORMAL)
		self.img = self._get_default_img()
		time.sleep(1)
		self.show(self.img)
		self.is_open = False

	def close(self):
		cv2.destroyAllWindows()
		self.is_open = False
		exit()

	def send(self, img):
		self.img = img

	def _get_default_img(self):
		filepath = os.path.join(os.path.expanduser("~"), '.local', 'np.jpeg')
		self.img = imutils.resize(cv2.imread(filepath), width=1024, height=768)
		return self.img
		
		
	def show(self, img=None):
		self.is_open = True
		if img is None:
			self.img = imutils.resize(self._get_default_img(), width=self.w, height=self.h)
		else:
			self.img = imutils.resize(img, width=self.w, height=self.h)
		cv2.imshow(self.name, self.img)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			self.close()
		if self.w is None and self.h is None:
			self.w, self.h = int(self.img.shape[1]), int(self.img.shape[0])
			cv2.resizeWindow(self.name, (self.w, self.h))

	def stop(self):
		self.cap.release()
		exit()


	def draw_on_image(self, img, boxes):
		w = img.shape[1]
		h = img.shape[0]
		drawn = img.copy()
		for box in boxes:
			object_name = 'Motion detected!'
			drawn = cv2.rectangle(img, (int(box.l), int(box.t)), (int(box.r), int(box.b)), box.color, 2)
			y = box.t + 30
			coords = (int(box.l), int(y))
			drawn = cv2.putText(drawn, object_name, coords, self.opts['FONT'], self.opts['FONT_SCALE'], BLUE, 2, cv2.LINE_AA)
		return drawn

	#get all current class properties (use instead of opts dict)
	def get_props(self):
		return self.__dict__

	#update class property to change functionality on the fly
	def set_props(self, prop, val=None):
		try:
			self.__dict__[prop] = val
			return True
		except Exception as e:
			log(f"DISPLAY_THREAD:{self.camera_id}:PROPERTY_SET:Var={prop}, Value:{val} Error:{e}", 'info')
			return False

if __name__ == "__main__":
	import sys
	try:
		camera_id = int(sys.argv[1])
	except:
		camera_id = 0
	from capture import *
	from display import display
	cap = capture(camera_id)
	d = display(camera_id, cap)
	d.run()
