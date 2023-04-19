from ptz_control import ptz_control
from conf import read_opts
from detector import *
from queue import Queue
from new_object import new_object
from capture_new import *

class analyze():
	def __init__(self, camera_id=None, cap=None, ptz=None):
		log(f"analyze.init:Initializing...", 'info')
		if camera_id is None:
			self.camera_id = 0
			log(f"analyze.init:No camera id provided, defaulting to 0", 'warning')
		else:
			self.camera_id = camera_id
		self.opts = read_opts(camera_id)
		if cap is None:
			self.cap = capture(self.camera_id)
		else:
			self.cap = cap
		self.ptz_enabled = self.opts['has_ptz']
		if self.ptz_enabled:
			if ptz is None:#if ptz object not provided, create ptz
				log(f"analyze.init:Created ptz object!", 'info')
				self.ptz = ptz_control(self.camera_id)
			else:
				log(f"analyze.init:ptz provided, skipping creation.", 'info')
				self.ptz = ptz
		else:#if ptz disabled, set to None whether provided as argument or not
			self.ptz = None
		self.d = detector(self.camera_id)
		self.runloop = False
		self.confidence = self.opts['detector']['object_detector']['confidence']
		log(f"analyze.init:Initialization complete!", 'info')
		self.skip_frames = 15
		self.current_frame = 0
		self.img = None
		self.dets = []
		self.run()

	def get_detection(self):	
		if self.dets != []:
			dets = self.dets
			ret = True
		else:
			ret = False
			dets = None
		self.dets = []
		return ret, dets

	def run(self):
		t = Thread(target=self._run)
		t.setDaemon(True)
		t.start()


	def _run(self):
		self.runloop = True
		log(f"analyze.run:Starting run loop (runloop={self.runloop})...", 'info')
		while self.runloop:
			ret, self.img = self.cap.read()
			if not ret:
				#log(f"analyze.run:No image data yet...", 'info')
				self.dets = []
			else:
				self.dets = self.d.detect(img=self.img, confidence=self.confidence)
