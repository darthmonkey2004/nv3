import os
from conf import *

class message(object):
	def __init__(self, camera_id=None, priority=5, data=None):
		self.camera_id = camera_id
		self.pid = os.getpid()
		self.name = __name__
		self.priority = priority
		self.data = data

class nvbox(message):
	def __init__(self, camera_id, box, class_name='Detection', img=None, confidence=None, float: tolerance=0, float: distance=0):
		self.camera_id = camera_id
		self.conf = readConf()
		self.class_name = class_name
		self.confidence = self.conf['cameras'][0]['detector']['object_detector']['confidence']
		self.tolerance = tolerance
		self.distance = distance
		self.img = img
		self.classes = ['background', 'aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus', 'car', 'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse', 'motorbike', 'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tvmonitor']
		self.animals = ['bird', 'cat', 'cow', 'dog', 'horse', 'sheep']
		self.vehicles = ['aeroplane', 'bicycle', 'boat', 'bus', 'car', 'motorbike', 'train']
		if box is not None:
			#completely initialize class (for detection subclass)
			self.new(box=box, class_name=self.class_name)
		else:
			raise Exception(ValueError, 'new_object.nvbox.init:Box cannot be None!')
		if self.class_name in classes:
			if self.class_name == 'person':
				self.type = 'person'
			else:
				if self.class_name not in animals and self.name not in vehicles:
					self.type = 'object'
				elif self.class_name in animals:
					self.type = 'animal'
				elif self.class_name in vehicles:
					self.type = 'vehicle'
		else:
			self.type = self.class_name
		self.opts = self.conf['cameras'][self.camera_id]
		if isinstance(box, nvbox):#if type is already nvbox, overwrite name and type, log possible stale box
			log(f"box.init: Box argument already of type 'nvbox', could be stale!", 'warning')
			box = box.box
			if self.class_name is None:
				self.class_name = box.class_name
				self.type = box.type
				
		#creates a new box
		if (box[2] - box[0]) < 0 or (box[3] - box[1]) < 0:# if w or h negative, it was probably a roi (x, y, w, h). So...
			self.l, self.t, self.w, self.h = box
			self.r = self.w + self.l
			self.b = self.h + self.t
			self.box = self.l, self.t, self.r, self.b
		else:
			self.l, self.t, self.r, self.b = box
			self.w = self.r - self.l
			self.h = self.b - self.t
			self.box = box
		self.tracker_box = self.l, self.t, self.w, self.h
		self.size = (self.h, self.w)
		self.color = (randint(0, 255), randint(0, 255), randint(0, 255))
		self.font = self.opts['FONT']
		self.font_scale = self.opts['FONT_SCALE']
		self.line_type = line_type
		self.line_size = 2
		self.cx = round((self.w / 2) + self.l)
		self.cy = round((self.h / 2) + self.t)
		self.center = (self.cx, self.cy)
		super().__init__(camera_id, 5, self.box)
