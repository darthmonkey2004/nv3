#https://learnopencv.com/multitracker-multiple-object-tracking-using-opencv-c-python/
#from __future__ import log_function
from log import nv_logger
import sys
import cv2
from random import randint
from conf import *
import numpy as np
from new_object import *
log = nv_logger().log_msg
txt = """
TODO:
	1. Re-organize multi_tracker class into a manager to track multiple objects.
	
"""
log(txt, 'info')
class tracker():
	def __init__(self, img, box, camera_id, class_name='Detection', tracker_type=None, confidence=None, max_age: int=200):
		self.camera_id = int(camera_id)
		#assume box is in l, t, r, b format, and convert to x, y, w, h
		box = self.box_to_trackerBox(box)
		self.conf = readConf()
		self.opts = self.conf['cameras'][self.camera_id]
		self.nvbox = new_object(camera_id=self.camera_id, object_name='box').new
		self.max_age = max_age
		#self.max_misses = self.opts['tracker']['max_misses']
		self.img = img
		self.class_name = class_name
		#self.misses = 0
		self.age = 0
		self.success = False
		self.types = read_opts(camera_id)['tracker']['types']['available']
		self.oldbox = None
		if tracker_type is None:
			tracker_type = self.opts['tracker']['types']['selected']
		else:
			tracker_type = tracker_type
		if confidence is None:
			self.confidence = self.opts['detector']['object_detector']['confidence']
		else:
			self.confidence = confidence
		self.camera_id = int(camera_id)
		if box[2] == 0 or box[3] == 0:
			txt = f"Empty box! (box={box})"
			raise Exception(ValueError, txt)
		self.tracker = self.new_tracker(camera_id=self.camera_id, tracker_type=tracker_type)
		if self.tracker.init(img, box):
			self.success, box = self.tracker.update(img)
			if self.success:
				try:
					#create new nvbox with conversion from (x, y, w, h) to (l, t, r, b).
					self.box = self.trackerBox_to_box(box)
				except Exception as e:
					txt = f"tracker.init:Exception occured creating nvbox item ({e})!"
					raise Exception('TrackerCreateFailed', txt)
			else:
				log = (f"tracker.init:Update failed!", 'info')
				return None
		else:
			log(f"tracker.init:Init failed for tracker!", 'error')
			return None
		self.color = (randint(0, 255), randint(0, 255), randint(0, 255))
		self.font = self.opts['FONT']
		self.font_scale = self.opts['FONT_SCALE']
		self.line_type = cv2.LINE_AA
		self.line_size = 2
		self.success = True
		self.area = None

	def update(self, img):
		self.age += 1
		self.img = img
		self.success, roibox = self.tracker.update(img)
		self.box = self.trackerBox_to_box(roibox)
		if self.oldbox is None:
			self.oldbox = self.box
		# if track fails...
		if not self.success:
			#log(f"Update tracker failed:{self.success}", 'info')
			#increment age counter if fail (accellerated aging)
			self.age += 1
		else:
			if self.oldbox == self.box:
				self.age += 1
				#log(f"tracker.update:Box is getting stale...(miss count:{self.age})", 'info')
			else:
				self.oldbox = self.box
				self.age = 0
				#log(f"tracker.update:Reset age!", 'info')
			cx = round((roibox[2] / 2) + roibox[0])
			cy = round((roibox[3] / 2) + roibox[1])
			# if centroid of box approaching end of screen...
			if cx <= 0 or cx >= self.img.shape[1] or cy <= 0 or cy >= self.img.shape[0]:
				log(f"tracker.update:Runaway target! This is where we'll chase 'em with ptz...(Adding a miss for now)")
				self.age += 1
			# if all things went well, update box and reset miss counter
			else:
				#convert box from (x, y, w, h) to (l, t, r, b)
				self.box = self.trackerBox_to_box(roibox)
				#self.age = 0
		if self.age >= self.max_age:
			log(f"tracker.update:Tracker expired!", 'info')
			self.success = False
			return self.success
		self.color = (randint(0, 255), randint(0, 255), randint(0, 255))
		self.font = self.opts['FONT']
		self.font_scale = self.opts['FONT_SCALE']
		self.line_type = line_type
		self.line_size = 2
		self.success = True
		self.box = self.nvbox(box=self.box, class_name=self.class_name, img=img)
		return self.success

			
	def trackerBox_to_box(self, tracker_box):
		self.l, self.t, self.w, self.h = tracker_box
		self.r = self.w + self.l
		self.b = self.h + self.t
		self.cx = round((self.w / 2) + self.l)
		self.cy = round((self.h / 2) + self.t)
		self.center = (self.cx, self.cy)
		self.area = self.w * self.h
		self.size = (self.w, self.h)
		return (int(self.l), int(self.t), int(self.r), int(self.b))

	def box_to_trackerBox(self, box):
		self.l, self.t, self.r, self.b = box
		self.w = self.r - self.l
		self.h = self.b - self.t
		self.cx = round((self.w / 2) + self.l)
		self.cy = round((self.h / 2) + self.t)
		self.center = (self.cx, self.cy)
		self.area = self.w * self.h
		self.size = (self.w, self.h)
		return (int(self.l), int(self.t), int(self.w), int(self.h))

	def set_max_age(self, age):
		self.max_age = int(age)
		log(f"tracker.set_max_age:Updated max age! ({self.max_age})")

	#def set_max_misses(self, num):
	#	self.max_misses = int(num)
	#	log(f"tracker.set_max_misses:Updated max misses limit! ({self.maX_age})")

	def new_tracker(self, camera_id, tracker_type=None):
		# Create a tracker based on tracker name
		if tracker_type == self.types[0]:
			return cv2.TrackerBoosting_create()
		elif tracker_type == self.types[1]:
			return cv2.TrackerMIL_create()
		elif tracker_type == self.types[2]:
			return cv2.TrackerKCF_create()
		elif tracker_type == self.types[3]:
			return cv2.TrackerTLD_create()
		elif tracker_type == self.types[4]:
			return cv2.TrackerMedianFlow_create()
		elif tracker_type == self.types[5]:
			return cv2.TrackerGOTURN_create()
		elif tracker_type == self.types[6]:
			return cv2.TrackerMOSSE_create()
		elif tracker_type == self.types[7]:
			return cv2.TrackerCSRT_create()
		else:
			tracker = None
			log(f"tracker.new_tracker:Tracker selection invalid: {tracker_type}! Defaulting to 'CSRT'...", 'warning')
			log('tracker.new_tracker:Available trackers are:')
			for t in self.types:
				log(t)
			return cv2.TrackerCSRT_create()
