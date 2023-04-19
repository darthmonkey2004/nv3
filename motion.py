from random import randint
import pickle
import time
import numpy as np
from cv2.bgsegm import createBackgroundSubtractorMOG, createBackgroundSubtractorGMG
from cv2 import createBackgroundSubtractorKNN, createBackgroundSubtractorMOG2, VideoCapture, destroyAllWindows, waitKey, imshow, WINDOW_AUTOSIZE, namedWindow, threshold, findContours, THRESH_BINARY, RETR_TREE, CHAIN_APPROX_SIMPLE, contourArea, drawContours, boundingRect, rectangle, cvtColor, COLOR_BGR2GRAY
import cv2
from log import nv_logger
log = nv_logger().log_msg


class nvbox():
	def __init__(self):
		self.w, self.h, self.l, self.t, self.r, self.b = 0, 0, 0, 0, 0, 0
		self.size = (self.w, self.h)
	def new(self, box):
		self.box = box
		self.l, self.t, self.r, self.b = self.box
		self.w = self.r - self.l
		self.h = self.b - self.t
		self.tracker_box = self.l, self.t, self.w, self.h
		self.size = (self.h, self.w)
		self.color = (randint(0, 255), randint(0, 255), randint(0, 255))
		self.cx = round((self.w / 2) + self.l)
		self.cy = round((self.h / 2) + self.t)
		self.center = (self.cx, self.cy)
		return self


class bs_detector():
	def __init__(self, **args):
		self.nvbox = nvbox()
		#init option defaults that will be overwritten by supplied arguments to ensure critical options are set (in case not provided by user)
		self.max_size = 50
		self.l = None
		self.t = None
		self.r = None
		self.b = None
		#w and h used in object tracker
		self.w = None
		self.h = None
		self.box = None
		self.history = 100
		self.thresh = 100
		self.retr_types = {'RETR_TREE': cv2.RETR_TREE, 'RETR_EXTERNAL': cv2.RETR_EXTERNAL}
		self.chain_approx_types = {'CHAIN_APPROX_SIMPLE': cv2.CHAIN_APPROX_SIMPLE, 'CHAIN_APPROX_TC89_KCOS': cv2.CHAIN_APPROX_TC89_KCOS, 'CHAIN_APPROX_TC89_L1': cv2.CHAIN_APPROX_TC89_L1, 'CHAIN_APPROX_NONE': cv2.CHAIN_APPROX_NONE}
		self.retr = self.set_retr()
		self.chain_approx = self.set_chain_approx()
		self.bs_types = ['KNN', 'MOG', 'MOG2', 'GMG']
		self.bs_list = self.init_bs()
		self.bs_type = 'MOG2'
		self.idx = int(self.bs_types.index(self.bs_type))
		self.bs = self.set_bs(self.idx)
		self.boxes = []
		# initialize class instance properties from supplied arguments.
		for key in list(args.keys()):
			self.__dict__[key] = args[key]


	def init_bs(self):
		self.bs_list = []
		for _type in self.bs_types:
			self.bs_list.append(self.create_bg_sub(_type))
		return self.bs_list


	def set_bs(self, idx=None):
		if idx is not None:
			self.idx = idx
		self.bs = self.bs_list[self.idx]
		return self.bs


	def create_bg_sub(self, _type=None, history=None, thresh=None):
		if _type is not None:
			_type = _type.upper()
			if _type in self.bs_types:
				self.bs_type = _type
			else:
				log(f"Unknown type: {_type}!", 'error')
				return None
		if history is not None:
			self.history = history
			log(f"Set background subtraction history length to {self.history}!", 'info')
		if thresh is not None:
			self.thresh = thresh
			log(f"Set Background subtraction threshold to {self.thresh}!", 'info')
		string = f"createBackgroundSubtractor{_type}"
		if self.bs_type == 'KNN' or _type == 'MOG':
			self.bs = globals()[string](history=self.history)
		elif self.bs_type == 'GMG':
			self.bs = globals()[string]()
		else:
			self.bs = globals()[string](history=self.history, varThreshold=self.thresh)
		return self.bs


	def set_chain_approx(self, _type='CHAIN_APPROX_NONE'):
		if _type in list(self.chain_approx_types.keys()):
			self.chain_approx = self.chain_approx_types[_type]
			return True
		else:
			j = "\n"
			log(f"Unknown CHAIN_APPROX type: {_type}! Available types: {j.join(list(self.chain_approx_types.keys()))}", 'error')
			return False
 
 
	def set_retr(self, _type='RETR_EXTERNAL'):
		if _type in list(self.retr_types.keys()):
			self.retr = self.retr_types[_type]
			return True
		else:
			j = "\n"
			log(f"Unknown RETR type: {_type}! Available types: {j.join(list(self.retr_types.keys()))}", 'error')
			return False

	def get_bigbox(self, contours, max_size=None):
		self.boxes = []
		if max_size is not None:
			self.max_size = max_size
		maxes_x = []
		maxes_y = []
		mins_x = []
		mins_y = []
		for item in contours:
			area = cv2.contourArea(item)
			if area > self.max_size:
				max_x, max_y = item.max(0)[0]
				if max_x != 0:
					maxes_x.append(max_x)
				if max_y != 0:
					maxes_y.append(max_y)
				min_x, min_y = item.min(0)[0]
				if min_x != 0:
					mins_x.append(min_x)
				if min_y != 0:
					mins_y.append(min_y)
		try:
			self.box = self.nvbox.new((sorted(mins_x)[0], sorted(mins_y)[0], sorted(maxes_x, reverse=True)[0], sorted(maxes_y, reverse=True)[0]))
			self.boxes = [self.box]
			return self.boxes
		except Exception as e:
			return []

	def get_bigbox2(self, contours):
		self.boxes = []
		newary = np.array(contours)
		maxes_x = []
		maxes_y = []
		mins_x = []
		mins_y = []
		for item in newary:
			max_x, max_y = item.max(0)[0]
			min_x, min_y = item.min(0)[0]
			maxes_x.append(max_x)
			maxes_y.append(max_y)
			min_x, min_y = item.min(0)[0]
			mins_x.append(min_x)
			mins_y.append(min_y)
			self.box = self.nvbox.new((sorted(mins_x)[0], sorted(mins_y)[0], sorted(maxes_x, reverse=True)[0], sorted(maxes_y, reverse=True)[0]))
			self.boxes.append(self.box)
		return self.boxes


	def clean(self, fg, max_size=None):
		if max_size is not None:
			self.max_size = max_size
		filtered = []
		_, fg = threshold(fg, 254, 255, THRESH_BINARY)
		contours, _ = findContours(fg, self.retr, self.chain_approx)
		if contours is not None and contours != []:
			try:
				return self.get_bigbox(contours, self.max_size)
			except Exception as e:
				print("Exception in clean():", e)
				return self.get_bigbox2(contours)
		else:
			return []


	def detect(self, img, max_size=None):
		#single shot, non loop detection
		if max_size is not None:
			self.max_size = int(max_size)
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		fg = self.bs.apply(img)
		return self.clean(fg, self.max_size)


	def loop(self, src=None):
		#optional internal loop for capture feed
		if src is None:
			log(f"Error: No source provided! Exiting...", 'error')
			exit()
		else:
			self.cap = cv2.VideoCapture(src)
		while True:
			ret, img = self.cap.read()
			if ret:
				self.boxes = self.detect(img)
				if len(self.boxes) > 0:
					for box in self.boxes:
						img = cv2.rectangle(img, (box.l, box.t), (box.r, box.b), box.color, 3)
				cv2.imshow('Image', img)
				k = cv2.waitKey(1)
				if k == 113:
					break
				elif k == 49:
					self.idx = 0
				elif k == 50:
					self.idx = 1
				elif k == 51:
					self.idx = 2
				elif k == 52:
					self.idx = 3
				else:
					self.idx = None
				if self.idx is not None:
					self.bs = self.select_bs(self.idx)
					log(f"Switched to {self.bs_types[self.idx]}!", 'info')
		self.cap.release()
		self.destroyAllWindows()




	def show(self, img):
		"""show single image and close window one-shot"""
		cv2.imshow('Image:', img)
		cv2.waitKey(0)
		cv2.destroyAllWindows()

if __name__ == "__main__":
	import sys
	try:
		ip_address = sys.argv[1]
	except:
		ip_address = '192.168.2.22'
	try:	
		port = sys.argv[2]
	except:
		port = 6969
	try:
		sound_profile = sys.argv[3]
	except:
		sound_profile = 'pcm'
	bsd = bs_detector()
	killwin = cv2.destroyAllWindows
	#auth_string = f"monkey:{bsd.get_auth()}"
	cv2.namedWindow("Image", cv2.WINDOW_AUTOSIZE)
	#src = f"rtsp://{auth_string}@{ip_address}:{port}/h264_{sound_profile}.sdp"
	src = 'rtsp://192.168.2.12/12'
	bsd.loop(src)
