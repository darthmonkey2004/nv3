from nv_ui import *
import numpy as np
import os
import cv2
from conf import *
from utils import *
from log import nv_logger
import threading
from nv_ui import *
from queue import Queue
from analyze import analyze
from threading import Thread
from multi_tracker import *
log = nv_logger().log_msg

txt = """
TODO: nv.py (.local nv3):
	1. determine if face recognition box and person detection box exist with overlap.
	2. test intersection/union (url1='https://answers.opencv.org/question/67091/how-to-find-if-2-rectangles-are-overlapping-each-other/')
	3. make union/intersection functions(url='https://answers.opencv.org/question/90455/how-to-perform-intersection-or-union-operations-on-a-rect-in-python/')
	def union(a,b):
	  x = min(a[0], b[0])
	  y = min(a[1], b[1])
	  w = max(a[0]+a[2], b[0]+b[2]) - x
	  h = max(a[1]+a[3], b[1]+b[3]) - y
	  return (x, y, w, h)
	
	def intersection(a,b):
	  x = max(a[0], b[0])
	  y = max(a[1], b[1])
	  w = min(a[0]+a[2], b[0]+b[2]) - x
	  h = min(a[1]+a[3], b[1]+b[3]) - y
	  if w<0 or h<0: return () # or (0,0,0,0) ?
	  return (x, y, w, h)
	
TODO: Tracker:
	1. implement into nv.py, using self.is_tracking and frame skip to avoid detection time.
	2. explore possibility of using centroid tracking, possibly create a centroid multi_tracker class
TODO: io/queue class object - handles reading and replacing message objects to the queue
	holds command, process (detection), and image feed queues.
	pass object to all threads, ensure each thread can get instructions/resources
	from that object ALONE.
	Opening communication/registration of sender/receiver:
		Needs to contain the pid of script file and thread type (object.thread_type property)
TODO: Clean up imports. either entire cv2 and specify targets with '.'s, or get anal and specify all of which we're using... no reason for both. Me bein' lazy.
TODO: integrate object tracking algorithm (centroid???)
TODO: PTZ():
	1. integrate serial servo controller
	2. integrate ipcamera ptz requests control
	3. design, implement, debug simulated ptz control via zoom/crop
	4. design, implement, debug virtual gamer/control 
"""
log(txt, 'info')
#input("READ FIRST!!! Press a key to continue...")
class nv(threading.Thread):
	def __init__(self, camera_id, cap=None, run_ui=True):
		self.run_ui = run_ui
		conf = readConf()
		if cap is None:
			src = conf['cameras'][camera_id]['src']['url']
			self.cap = cv2.VideoCapture(src)
		else:
			self.cap = cap.cap
		self.camera_id = camera_id
		self.opts = conf['cameras'][self.camera_id]
		self.processing = self.opts['processing']
		self.fps = 30
		self.w = None
		self.h = None
		self.maxsize = None
		self.has_ptz = self.opts['has_ptz']
#		if self.ptz == None:
#			self.ptz = ptz_control()
#			self.ptz.set_speed(self.ptz_speed)
#		else:
#			self.ptz = None
#		if self.run_ui:
#			print("Running ui..")
#			self.ui = self.start_ui()
#			print("Ui running!")
#		if self.has_ptz:
#			self.ui.ptz.events = True
#			self.preset = None
#			tour_dest = 0
		self.runloop = False
		if self.processing:
			self.det_thread = self.setup_detection()
		else:
			self.det_thread = None
		self.tryct = 500
		self.tries = 0
		self.is_tracking = False
		self.mt = multi_tracker(camera_id=self.camera_id)
		self.trackers = {}
		log(f"nv.init():Display loop initialized!", 'info')


	def setup_detection(self):
		self.maxsize = self.opts['maxsize']
		self.in_q = Queue(maxsize=self.maxsize)
		self.out_q = Queue(maxsize=self.maxsize)
		#if self.has_ptz:
		#	if self.ui.ptz is None:
		#		self.ui.ptz = ptz_control(self.camera_id)
		#	t = Thread(target=analyze, args=(self.camera_id,self.in_q,self.out_q,self.ui.ptz))
		#else:
		t = Thread(target=analyze, args=(self.camera_id,self.in_q,self.out_q))
		t.setDaemon(True)
		return t

	def det_send(self, img):
		if not self.in_q.full():
			self.in_q.put_nowait(img)
			return True
		else:
			if self.tries <= self.tryct:
				self.tries += 1
				#print(f"attempts:{self.tries}/{self.tryct}, full:{self.in_q.full()}, empty:{self.in_q.empty()}, unfinished:{self.in_q.unfinished_tasks}, maxsize:{self.in_q.maxsize}, qsize:{self.in_q.qsize()}")
				return True
			elif self.tries == self.tryct:
				log(f"nv.det_send:Detection input has been too full, too long! This taint good...", 'error')
				try:
					while not self.in_q.empty():
						self.in_q.get_nowait()
						self.in_q.task_done()
					log(f"nv.det_send:Detection queue cleared!", 'warning')
					return True
				except Exception as e:
					txt = f"nv.det_send:Tried to clear queue, failed, wtf????"
					raise Exception('Shit Be Broken', txt)

	def det_recv(self):
		if not self.out_q.empty():
			dets = self.out_q.get_nowait()
			try:
				self.out_q.task_done()
				return True, dets
			except Exception as e:
				log(f"nv.det_recv:Got image but couldn't flag as finished! Unknown error ({e})", 'error')
				return False, None
		else:
			return False, None

	def test_inner(self, det1, det2):
		#tests whether one box is inside another. (tracking a face and the person at the same time
		if det1.area > det2.area:#test which box is larger, identify each
			outer = det1
			inner = det2
		elif det2.area > det1.area:
			outer = det2
			inner = det1
		
		#if coordinates of inner exists completely inside of outer, then it's a face.
		if inner.l >= outer.l and inner.r <= outer.r and inner.t >= outer.t and inner.b <= outer.b:
			#set detected face name to person detection's class_name (overwrite)
			outer.class_name = inner.class_name
			return True, outer
		else:
			return False, None


	def nv_run(self):
		self.nv_thread = Thread(target=self.run)
		self.nv_thread.setDaemon(True)
		self.nv_thread.start()
		
		
	def run(self):
		if self.processing:
			self.det_thread.start()
		log(f"nv.init():Starting nv loop...", 'info')
		cv2.namedWindow('image', cv2.WINDOW_NORMAL)
		log(f"nv.init():Display loop started!", 'info')
		self.runloop = True
		while self.runloop:
			ret, img = self.cap.read()
			if ret:
				if self.processing:
					if not self.is_tracking:
						ret = self.det_send(img)
						if not ret:
							log(f"nv.run:Unable to send to detector! Aborting...", 'error')
							self.runloop = False
							break
						dret, dets = self.det_recv()
						if dret:
							newdets = []
							for det in dets:
								#print("detection type:", det.type)
								self.is_tracking, self.trackers = self.mt.add(img=img, box=det.box, class_name=det.class_name, confidence=det.confidence, max_age=174)
								if self.is_tracking and self.trackers != {}:
									img = self.draw_on_image(img, self.trackers)
					else:#if currently tracking an object...
						self.is_tracking, self.trackers = self.mt.update(img=img)
						#print("tracking:", self.is_tracking)
						if self.is_tracking:
							img = self.draw_on_image(img, self.trackers)
				cv2.imshow('image', img)
				if cv2.waitKey(1) & 0xFF == ord('q'):
					self.stop()
					break
				if self.w is None and self.h is None:
					self.w, self.h = int(img.shape[1]), int(img.shape[0])
					cv2.resizeWindow('image', (self.w, self.h))

	def stop(self):
		self.cap.release()
		exit()


	def draw_on_image(self, img, trackers=None):
		if trackers is None:
			trackers = self.trackers
		w = img.shape[1]
		h = img.shape[0]
		drawn = img.copy()
		for tid in trackers.keys():
			t = trackers[tid]
			#print(f"box={t.box}, name={t.class_name}, size={t.size}, center={t.center}, area={t.area}")
			drawn = cv2.rectangle(img, (int(t.l), int(t.t)), (int(t.r), int(t.b)), t.color, t.line_size)
			y = t.t - 30
			coords = (int(t.l), int(y))
			drawn = cv2.putText(drawn, t.class_name, coords, t.font, t.font_scale, t.color, t.line_size, t.line_type)
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
	from nv import nv
	cap = capture(camera_id)
	d = nv(camera_id, cap)
	d.nv_run()
	#ui = nv_ui(camera_id)
	while True:
		#ui.ui_loop()
		pass
