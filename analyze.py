from ptz_control import ptz_control
from conf import read_opts
from detector import *
from queue import Queue
from new_object import new_object

class analyze():
	def __init__(self, camera_id=None, in_q=None, out_q=None, ptz=None):
		log(f"analyze.init:Initializing...", 'info')
		if camera_id is None:
			self.camera_id = 0
			log(f"analyze.init:No camera id provided, defaulting to 0", 'warning')
		else:
			self.camera_id = camera_id
		self.opts = read_opts(camera_id)
		if in_q is None:
			log(f"analyze.init:No input q provided! Creating dummy queue...")
			self.in_q = Queue(maxsize=30)
		else:
			self.in_q = in_q
		if out_q is None:
			log(f"analyze.init:No output q provided! Creating dummy queue...")
			self.out_q = Queue(maxsize=30)
		else:
			self.out_q = out_q
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
		self.skip_frames = 30
		self.current_frame = 0
		self.run()

	def read(self):
		if not self.in_q.empty():
			self.img = self.in_q.get_nowait()
			self.in_q.task_done()
			#print("grabbed image")
			return True, self.img
		else:
			return False, None

	def set_prop(self, string):
		if '=' in string:
			key = string.split('=')[0]
			val = string.split('=')[1]
		else:
			key = string
			val = None
		try:
			self.__dict__[key] = val
			log(f"analyze.set_prop:set property {key} to {val}!", 'info')
			return True
		except Exception as e:
			log(f"analyze.set_prop:Unable to set property ({key}, {val}): {e}", 'error')
			return False


	def send(self, data):
		if not self.out_q.full():
			self.out_q.put_nowait(data)
			print("put detection")
			return True

	def command_handler(self, com=None):
		if com is None:
			com = self.command
		if self.command is not None:
			if self.command == 'set' or self.command == 'set_prop':
				ret = self.set_prop(self.command)
				if ret:
					msg = new_object(object_name='message', camera_id=self.camera_id).new(data=f"property set: {self.command}")
				else:
					msg = new_object(object_name='message', camera_id=self.camera_id).new(data=f"set property failed!")
				self.send(msg)
			else:
				log(f"analyze.command_handler:TODO - FINISH ME!!!!!", 'info')
				return False
		else:
			log(f"analyze.command_handler:Command is null: {com}!", 'info')
			return False

	def scale_box(self, sm_img, big_img, sm_box):
		y_ = big_img.shape[0]
		x_ = big_img.shape[1]
		target_x = sm_img.shape[1]
		target_y = sm_img.shape[0]
		x_scale = target_x / x_
		y_scale = target_y / y_
		x = int(np.round(sm_box[0] / x_scale))
		y = int(np.round(sm_box[1] / y_scale))
		xmax = int(np.round(sm_box[2] / x_scale))
		ymax = int(np.round(sm_box[3] / y_scale))
		return x, y, xmax, ymax

	def run(self):
		self.runloop = True
		log(f"analyze.run:Starting run loop (runloop={self.runloop})...", 'info')
		while self.runloop:
			ret, img = self.read()
			if ret:
				orig = img.copy()
				img = imutils.resize(img, width=300)
				if isinstance(img, nvbox):
					img = self.img.data
				elif type(img.data) == str:
					self.command = img.data
					log(f"analyze.run:Command received! com={self.command}", 'info')
					if self.command == 'quit':
						log(f"analyze.run:Quit command received! Exiting...", 'info')
						self.runloop = False
						break
					else:
						ret = self.command_handler(self.command)
						log(f"analyze.run:TODO - create and implement command_handler function", 'warning')
				self.current_frame += 1
				if self.current_frame == self.skip_frames and img is not None:
					self.current_frame = 0
					dets = self.d.detect(img=img, confidence=0.3)#0.49 is default, opts['detector']['object_detector']['confidence']
					if dets != []:
						for det in dets:
							det.box = self.scale_box(img, orig, det.box)
							det.l, det.t, det.r, det.b = det.box
							det.w = det.r - det.l
							det.h = det.b - det.t
							det.tracker_box = det.l, det.t, det.w, det.h
						self.send(dets)
