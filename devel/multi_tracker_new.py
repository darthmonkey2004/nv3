#https://learnopencv.com/multitracker-multiple-object-tracking-using-opencv-c-python/
#from __future__ import log_function
from log import nv_logger
import sys
import cv2
#from random import randint
from conf import *
import numpy as np
#from new_object import *
log = nv_logger().log_msg
from tracker_new import *


class multi_tracker():
	def __init__(self, camera_id):
		self.camera_id = camera_id
		self.opts = read_opts(self.camera_id)
		self.trackers = {}

	def add(self, img, det, tracker_type=None, max_age: int=200):
		if tracker_type is not None:
			self.tracker_type = tracker_type
		else:
			self.tracker_type = self.opts['tracker']['types']['selected']
		self.max_age = max_age
		idx = len(list(self.trackers))
		t = tracker(img=img, det=det, tracker_type=self.tracker_type, max_age=self.max_age)
		if t.success:
			self.trackers[idx] = t
			log(f"Added tracker: {idx}!")
			return True, self.trackers
		else:
			log(f"Init failed for tracker!")
			return False, None


	def update(self, img):
		todel = []
		tokeep = []
		ret = False
		for tid in self.trackers.keys():
			t = self.trackers[tid]
			ret = t.update(img)
			# if track fails...
			if not ret:
				todel.append(tid)
		for tid in todel:
			del self.trackers[tid]
		if self.trackers == {}:
			ret = False
		return ret, self.trackers


	def clear(self):
		todel = list(self.trackers.keys())
		for tid in todel:
			del self.trackers[tid]
		log(f"All tracker data cleared!")
