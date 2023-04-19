import keyring
import getpass
import sys
import os
import subprocess
import requests
import base64
import time
import pickle
from conf import *
from log import nv_logger
from new_object import new_object

log = nv_logger().log_msg



class ptz_control():
	def __init__(self, camera_id=None):
		print("camera_id:", camera_id)
		if camera_id is None:
			txt = f"ptz_control.init:ERROR! Camera_id CANNOT be None!"
			raise Exception(ValueError, txt)
		else:
			self.camera_id = camera_id
		message = new_object(camera_id=self.camera_id, object_name='message')
		self.opts = read_opts(camera_id)
		self.headers = {}
		self.base_path = self.opts['ptz']['base_path']
		self.param_endpoint = self.opts['ptz']['param_endpoint']
		self.control_endpoint = self.opts['ptz']['control_endpoint']
		if self.opts['ptz']['addr'] is None:
			self.opts['ptz']['addr'] = input("Enter remove camera ip:")
			self.addr = self.opts['ptz']['addr']
			write_opts(camera_id=camera_id, opts=opts)
		else:
			self.addr = self.opts['ptz']['addr']
		self.speeds = [0, 1, 2]
		self.speeds_names = ['high', 'medium', 'low']
		self.uses_auth = self.opts['ptz']['auth']['uses_auth']
		self.user = self.opts['ptz']['auth']['user']
		self.event_loop = self.opts['ptz']['events']
		self.key = None
		self.action = None
		self.base_url = f"http://{self.addr}/{self.base_path}"
		self.stop_command = f"-step=0&-act=stop"
		self.stop_url = f"{self.create_url(type='control')}?{self.stop_command}"
		self.directions = ['left', 'downleft', 'down', 'downright', 'right', 'upright', 'up', 'upleft', 'stop']
		self.s = {}
		self.s[0] = 0, 1
		self.s[1] = 0.1 , 1
		self.s[2] = 0.5, 1
		self.s[3] = 1, 1
		self.s[4] = 0.1, 1
		self.s[5] = 0.5, 1
		self.s[6] = 1, 1
		self.s[7] = 0.1, 1
		self.s[8] = 0.5, 1
		self.s[9] = 1, 1
		self.pan_speed = 1
		self.tilt_speed = 1
		self.track_to_center = self.opts['detector']['track_to_center']
		self.thread_type = 'ptz_control'
		self.pid = os.getpid()
		# if authentication used, modify empty headers dictionary to use basic auth
		if self.uses_auth is True:
			pw = self.get_pass(addr=self.addr, user=self.user)
			if pw is None:
				self.set_pass(self.user)
				pw = self.get_pass()
			string=f"{self.user}:{pw}".encode('ascii')
			self.headers = {}
			self.headers["Authorization: Basic"] = base64.b64encode(string).decode()


	def get_current_options(self):
		self.base_url
		url = f"{self.base_url}/param.cgi?cmd=getvencattr&-chn=11&cmd=getvencattr&-chn=12&cmd=getsetupflag&cmd=getvideoattr&cmd=getimageattr&cmd=getinfrared&cmd=getserverinfo&cmd=getmotorattr&cmd=getinfrared&cmd=getrtmpattr"

	

	def set_ptz_track_to_center(self, val=False):
		self.track_to_center = val
		self.opts['detector']['track_to_center'] = self.track_to_center
		write_opts(self.opts)
		log(f"Track to center: {self.track_to_center}", 'info')


	def send(self, url):
		if self.uses_auth is True:
			pw = self.get_pass(addr=self.addr, user=self.user)
			ret = requests.get(url, auth=(self.user, pw))
		else:
			ret = requests.get(url)
		if ret.status_code == 200:
			return True
		else:
			log(f"Error: Bad status code: {ret.status_code}", 'error')
			return False


	def create_url(self, type=None):
		if type == 'control':
			url = f"{self.base_url}/{self.control_endpoint}"
		elif type == 'param':
			url = f"{self.base_url}/{self.param_endpoint}"
		return url


	def set_speed(self, pan_spd=None, tilt_spd=None):
		if pan_spd is not None:
			self.pan_speed = int(pan_spd)
		if tilt_spd is not None:
			self.tilt_speed = int(tilt_spd)
		if self.pan_speed > 2:
			self.pan_speed = 2
		elif self.pan_speed < 0:
			self.pan_speed = 0
		if self.tilt_speed > 2 :
			self.tilt_speed = 2
		elif self.tilt_speed < 0:
			self.tilt_speed = 0
		set_command = f"cmd=setmotorattr&-tiltspeed={self.tilt_speed}&-panspeed={self.pan_speed}"
		url = f"{self.create_url(type='param')}?{set_command}"
		self.send(url)

	def get_pass(self, addr=None, user=None):
		if addr is None:
			addr = get_local_ip()
		if user is None:
			user = os.path.expanduser("~").split('/home/')[1]
		pw = keyring.get_password(addr, user)
		if pw is None:
			pw = self.set_pass(addr=addr, user=user)
		return pw


	def set_pass(self, addr=None, user=None, pw=None):
		if addr is None:
			addr = get_local_ip()
		if user is None:
			user = os.path.expanduser("~").split('/home/')[1]
		if pw is None:
			import getpass
			pw = str(getpass.getpass("Enter ip camera password: "))
		if pw is not None:
			keyring.set_password(addr, user, pw)
			return pw
		else:
			log(f"Error: Couldn't set password!")
			return None

	def goto(self, num):
		set_command = f"cmd=preset&-act=goto&-number={num}"
		url = f"{self.create_url(type='param')}?{set_command}"
		self.send(url)


	def set_goto(self, num):
		set_command = f"cmd=preset&-act=set&-status=1&-number={num}"
		url = f"{self.create_url(type='param')}?{set_command}"
		log(f"pts_control.set_goto():url={url}", 'info')
		self.send(url)


	def step(self, d=None, wait=1):
		directions = ['left', 'downleft', 'down', 'downright', 'right', 'upright', 'up', 'upleft']
		if d is None:
			d = input("Enter direction:")
		if d not in self.directions:
			log(f"Unknown direction: {d}", 'info')
		else:
			self.action = f"{self.create_url(type='control')}?-step=0&-act={d}"
			self.send(self.action)
			time.sleep(wait)
			self.action = f"{self.create_url(type='control')}?-step=0&-act=stop"
			self.send(self.action)


	def move(self, d=None):
		if d not in self.directions:
			log(f"Unknown direction: {d}", 'info')
			return False
		else:
			self.action = f"{self.create_url(type='control')}?-step=0&-act={d}"
			self.send(self.action)

	
if __name__ == "__main__":
	import sys
	try:
		act = sys.argv[1]
	except:
		log("Error: No arguments given!", 'info')
		exit()
	try:
		arg1 = sys.argv[2]
	except:
		arg1 = None

	ptz = ptz()
	
