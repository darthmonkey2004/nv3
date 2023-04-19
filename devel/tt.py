from detector import *
from capture_new import *
import cv2
from new_object import *

class tracker():
	def __init__(self, img, det, max_age=50, tracker_type=None):
		self.max_age = max_age
		self.age = 0
		if not isinstance(det, nvbox):
			txt = f"tracker.init:ERROR! Object is not a nvbox!"
			raise Exception(TypeError, txt)
		fields = ['animals', 'area', 'b', 'box', 'camera_id', 'center', 'class_name', 'classes', 'color', 'conf', 'confidence', 'cx', 'cy', 'data', 'distance', 'font', 'font_scale', 'h', 'img', 'l', 'line_size', 'line_type', 'name', 'opts', 'pid', 'priority', 'r', 'size', 't', 'tolerance', 'tracker_box', 'type', 'vehicles', 'w']
		for field in fields:
			try:
				self.__dict__[field] = det.__dict__[field]
			except:
				pass
		self.tracker_types = self.opts['tracker']['types']['available']
		print(self.tracker_types)
		if tracker_type is None:
			self.tracker_type = self.opts['tracker']['types']['selected']
		else:
			self.tracker_type = tracker_type
		self.img = img
		self.tracker = self.new_tracker(self.tracker_type)
		self.oldbox = None
		if self.tracker.init(self.img, self.box):
			self.success, self.tracker_box = self.tracker.update(self.img)
			self.box = self.trackerBox_to_box(self.tracker_box)
			return
		else:
			self.success = False
			log(f"Tracker failed to init!")
			return
	
	def update(self, img):
		self.age += 1
		self.img = img
		self.success, self.tracker_box = self.tracker.update(img)
		if self.tracker_box[2] == 0 or self.tracker_box[3] == 0:
			self.success = False
			return self.success
		if self.tracker_box == (0, 0, 0, 0):
			self.success = False
			return self.success
		self.box = self.trackerBox_to_box(self.tracker_box)
		if self.oldbox is None:
			self.oldbox = self.box
		# if track fails...
		if not self.success:
			#log(f"Update tracker failed:{self.success}", 'info')
			#increment age counter if fail (accellerated aging)
			#self.age += 1
			self.success = False
		else:
			if self.oldbox == self.box:
				self.age += 1
				#log(f"tracker.update:Box is getting stale...(miss count:{self.age})", 'info')
			else:
				self.oldbox = self.box
				self.age = 0
				#log(f"tracker.update:Reset age!", 'info')
			cx = round((self.tracker_box[2] / 2) + self.tracker_box[0])
			cy = round((self.tracker_box[3] / 2) + self.tracker_box[1])
			# if centroid of box approaching end of screen...
			if cx <= 0 or cx >= self.img.shape[1] or cy <= 0 or cy >= self.img.shape[0]:
				log(f"tracker.update:Runaway target! This is where we'll chase 'em with ptz...(Failing for now)")
				self.success = False
			# if all things went well, update box and reset miss counter
			else:
				#convert box from (x, y, w, h) to (l, t, r, b)
				self.box = self.trackerBox_to_box(self.tracker_box)
				#self.age = 0
		if self.age >= self.max_age:
			log(f"tracker.update:Tracker expired!", 'info')
			self.success = False
			return self.success
		self.success = True
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

	def new_tracker(self, tracker_type=None):
		# Create a tracker based on tracker name
		if tracker_type == self.tracker_types[0]:
			t = cv2.TrackerBoosting_create()
		elif tracker_type == self.tracker_types[1]:
			t = cv2.TrackerMIL_create()
		elif tracker_type == self.tracker_types[2]:
			t = cv2.TrackerKCF_create()
		elif tracker_type == self.tracker_types[3]:
			t = cv2.TrackerTLD_create()
		elif tracker_type == self.tracker_types[4]:
			t = cv2.TrackerMedianFlow_create()
		elif tracker_type == self.tracker_types[5]:
			t = cv2.TrackerGOTURN_create()
		elif tracker_type == self.tracker_types[6]:
			t = cv2.TrackerMOSSE_create()
		elif tracker_type == self.tracker_types[7]:
			t = cv2.TrackerCSRT_create()
		else:
			tracker = None
			log(f"tracker.new_tracker:Tracker selection invalid: {tracker_type}! Defaulting to 'CSRT'...", 'warning')
			log('tracker.new_tracker:Available trackers are:')
			for t in types:
				log(t)
			t = cv2.TrackerCSRT_create()
		return t

if __name__ == "__main__":
	cap = capture(3)
	newbox = new_object(camera_id=3, object_name='box').new
	d = detector(camera_id=3)
	while True:
		ret, img = cap.read()
		if ret:
			dets = d.detect(img)
			for det in dets:
				t = tracker(det)
				print(dir(t))
