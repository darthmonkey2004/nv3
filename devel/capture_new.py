#This is a class that will initialize a cv2 VideoCapture device and multiplex it out to a list of pipelines provided
#expects all input/output in the form of the below message class. to be used with io.py
#by the parent object.
import imutils
import os
import sys
import cv2
from conf import *
from utils import get_auth, set_auth
import time
from threading import Thread
from log import nv_logger
from mss import mss
import numpy
log = nv_logger().log_msg


#https://python-mss.readthedocs.io/examples.html


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
				if self.img.shape[1] > 1024:
					self.img = imutils.resize(self.img, width=1024)
			except Exception as e:
				self.img = None
				log(f"screencap.read():Exception! ({e})", 'error')
				break
		self.img = None
		return

	def _start(self):
		try:
			self.t = Thread(target=self._capture)
			self.t.setDaemon(True)
			self.t.start()
			return True
		except Exception as e:
			log(f"capture._start():Failed to start thread:{e}", 'error')
			return False

	def read(self):
		img = self.img
		if img is None:
			return False, None
		else:
			return True, img

	def release(self):
		self.runloop = False



class capture():
	def __init__(self, camera_id=0):
		self.camera_id = camera_id
		conf = readConf()
		try:
			opts = conf['cameras'][self.camera_id]
		except:
			try:
				n = int(src)
			except:
				n = str(src)
			opts = init_opts(src=n, camera_id=self.camera_id, ptz=False, _type='cv2', has_auth=False)
			write_opts(camera_id=self.camera_id, opts=opts)
			conf = readConf()
		self.opts = conf['cameras'][self.camera_id]
		self.src = self.opts['src']['url']
		self.has_auth = self.opts['src']['has_auth']
		self.user = self.opts['src']['user']
		if self.has_auth:
			pw = get_auth(self.camera_id)
			src = self.opts['src']['url']
			self.src = f"rtsp://{self.user}:{pw}@{src.split('://')[1]}"
		self.exit = False
		self.is_capturing = False
		self.is_connected = False
		self.error = None
		self.fail_max = 30
		self.fail_ct = 0
		self.src_type = self.opts['src']['type']
		self.cap = self.get_capture()
		self.all_filters = ['jet', 'gray', 'inferno', 'viridis', 'negative']
		self.filters = []
		self.name = __name__
		self.run_loop = True
		log(f"capture.init():Capture initialized!", 'info')
		self.run()


	def add_filter(self, f):
		if type(f) == int:
			_filter = self.all_filters[f]
		elif type(f) == str:
			_filter = self.all_filters[self.all_filters.index(f)]
		if _filter not in self.filters:
			self.filters.append(_filter)
		return self.filters

	def remove_filter(self, f):
		if type(f) == int:
			_filter = self.all_filters[f]
		elif type(f) == str:
			_filter = self.all_filters[self.all_filters.index(f)]
		if _filter in self.filters:
			self.filters.remove(_filter)
		return self.filters

	def read(self):
		if self.img is not None:
			return True, self.img
		else:
			return False, None

	def release(self):
		try:
			self.cap.release()
			self.img = None
			self.run_loop = False
			log(f"capture.release:Capture device released!")
			return True
		except Exception as e:
			log(f"capture.release:Unable to release! ({e})", 'error')
			return False

	def run(self):
		log(f"capture.run:Capture starting...", 'info')
		self.run_loop = True
		if self.cap is not None:
			#if capture is good, start loop
			t = Thread(target=self._run)
			t.setDaemon(True)
			t.start()
			log(f"capture.run:Thread started!", 'info')
		else:
			log(f"Error: Capture is none! Aborting...", 'error')
			return None

	def _run(self):
		while self.run_loop:
			ret, img = self.cap.read()
			if ret:
				self.img = img
			else:
				self.img = None


	def get_capture(self, camera_id=None):
		if camera_id is not None:
			self.camera_id = camera_id
		if self.src_type == 'cv2':
			try:
				cap = cv2.VideoCapture(self.src)
				self.error = None
			except Exception as e:
				self.error = e
				log(f"Error: Couldn't get capture device: {self.error}", 'error')
				return None
		elif self.src_type == 'screen_grab':
			cap = screencap(self.camera_id)
			self.error = None
			time.sleep(1)
		ret, img = cap.read()
		if ret:
			self.is_connected = True
		else:
			log(f"Camera initialized, but couldn't get image!", 'warning')
			self.connected = False
		if self.is_connected:
			self.cap = cap
			return self.cap
		else:
			self.error = f"Unknown error: is_connected returned False!"
			return None
		
			


	def apply_filters(self, img):
		for _filter in self.filters:
			if _filter == 'jet':
				img = cv2.applyColorMap(img, cv2.COLORMAP_JET)
			elif _filter == 'gray':
				img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
			elif _filter == 'inferno':
				img = cv2.applyColorMap(img, cv2.COLORMAP_INFERNO)
			elif _filter == 'viridis':
				img = cv2.applyColorMap(img, cv2.COLORMAP_VIRIDIS)
			elif _filter == 'negative':
				img = 1 - img
		return img


	def quit(self):
		self.exit = True # if quit ran from parent, set self.exit to True to break above loop.
		# if capture still intialized...
		if self.cap is not None:
			self.cap.release()
			self.cap = None
			log(f"Capture released!", 'info')
		self.is_connected = False
		self.is_capturing = False
		#terminate thread
		exit()

	def command_handler(self, com):
		if isinstance(com, message):
			com = com.data
		if com == 'quit':
			log(f"capture.command_handler():quit command received!", 'info')
			self.cap.release()
			self.quit()
		if com == 'reinit':# if reinit, release and re initialize capture.
			#break current loop, but not exit.
			self.run_loop = False
			self.cap.release()
			log(f"MULTIPLEXER:command_hanlder(reinit):Capture released!", 'info')
			log(f"MULTIPLEXER:command_hanlder(reinit):Waiting 3 secs...", 'info')
			time.sleep(1)
			log(f"MULTIPLEXER:command_hanlder(reinit):Waiting 2 secs...", 'info')
			time.sleep(1)
			log(f"MULTIPLEXER:command_hanlder(reinit):Waiting 1 secs...", 'info')
			time.sleep(1)
			log(f"MULTIPLEXER:command_hanlder(reinit):Reinitializing capture...", 'info')
			self.cap = self.get_capture()
			if self.cap is not None:
				log(f"MULTIPLEXER:command_hanlder(reinit):Capture re-initialized! Resuming loop...", 'info')
				ret = self.start_loop()
				if ret:
					log(f"MULTIPLEXER:command_hanlder(reinit):Sucess!", 'info')
				else:
					log(f"MULTIPLEXER:command_hanlder(reinit):Unable to re-init capture device. Exiting...", 'error')
					self.quit()
			elif self.cap is None:
				self.error = f"Device capture requests returned none! Aborting..."
				log(f"MULTIPLEXER:command_hanlder(reinit):{self.error}", 'error')
				self.quit()
		elif 'add_filter' in com:
			_filter = com.split('=')[1]
			self.add_filter(_filter)
			log(f"MULTIPLEXER:command_hanlder(add_filter):Filter added ({_filter})!", 'info')
		elif 'remove_filter' in com:
			_filter = com.split('=')[1]
			self.remove_filter(_filter)
			log(f"MULTIPLEXER:command_hanlder(add_filter):Filter removed ({_filter})!", 'info')

if __name__ == "__main__":
	pass
