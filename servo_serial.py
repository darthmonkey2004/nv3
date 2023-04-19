import serial
import subprocess
from log import nv_logger
from keymap import ctk
import sys
from message import message

logger = nv_logger().log_msg
def log(msg, _type=None):
	if _type is None:
		_type = 'info'
	if _type == 'error':
		exc_info = sys.exc_info()
		logger(msg, _type, exc_info)
		return
	else:
		logger(msg, _type)

def get_dev():
	com = "ls /dev/ttyACM*"
	devs = subprocess.check_output(com, shell=True).decode().strip().split("\n")
	if len(devs) == 0:
		log(f"Unable to find serial! Exiting...", 'error')
		exit()
	elif len(devs) == 1:
		return devs[0]
	else:
		pos = -1
		for dev in devs:
			pos += 1
			print(f"{pos}. {dev}")
		no = input("Enter a device number: ")
		return devs[no]

class servo():
	def __init__(self, dev='/dev/ttyACM0', baud=115200):
		self.dev = dev
		self.baud = baud
		self.arduino = self.new_controller(self.dev, self.baud)
		if self.arduino is None:
			log("Failed to get device! Exiting...", 'error')
			exit()
		self.command = None
		self.com = {}
		self.com['pan'] = 1
		self.com['tilt'] = 2
		self.com['fire'] = 3
		self.get_response = False
		self.pos_max = 179
		self.pos_min = 1
		self.pos_center = 90
		self.pos_x = self.pos_center
		self.pos_y = self.pos_center
		self.event_loop = True
		self.key = None
		self.codes = list(ctk.keys())
		self.keys = list(ctk.values())
		self.step = 10
		self.thread_type = 'serial_ctl'
		self.pid = os.getpid()

	def move(self, servo, pos=None):
		if type(servo) == str:
			servo = self.com[servo]
		if pos is not None:
			if pos > self.pos_max:
				pos = self.pos_max
			elif pos < self.pos_min:
				pos = self.pos_min
		if type(servo) == str:
			servo = com[servo]
		if servo == 1:
			self.pos_x = pos
		elif servo == 2:
			self.pos_y = pos
		command = f"{servo}:{pos}\n"
		ret = self.send(command)
		log(ret, 'info')
			

	def new_controller(self, dev=None, baud=None):
		if dev is not None:
			self.dev = dev
		if baud is not None:
			self.baud = baud
		try:
			self.arduino = serial.Serial(self.dev, self.baud)
			return self.arduino
		except Exception as e:
			log(f"Unable to get device {self.dev} with baud {baud}: {e}", 'error')
			self.arduino = None

	def read(self):
		return str(self.arduino.readline())

	def send(self, command):
		self.command = command.encode()
		try:
			self.arduino.write(self.command)
		except:
			log("Obtaining write permissions...", 'info')
			ret = self.make_writeable(self.dev)
			if ret:
				self.arduino.write(self.command)
			else:
				log("Epic fail! Exiting...", 'error')
				exit()
		if self.get_response:
			out = str(self.arduino.readline())
		else:
			out = "Command Executed!"
		return out

	def make_writeable(self, dev=None):
		if dev is not None:
			self.dev = dev
		ret = subprocess.check_output(f"sudo chmod a+rwx \"{self.dev}\"", shell=True).decode().strip()
		if ret is not None and ret != '':
			log("Encountered error attempting to gain write access to device \'{self.dev}\'!", 'error')
			return False
		else:
			log("Ok!", 'info')
			return True

	def start_loop(self):
		try:
			from threading import Thread
			t = Thread(target=self.move-loop)
			t.setDaemon(True)
			t.start()
			log("Event loop started!", 'info')
			return True
		except Exception as e:
			log(f"Couldn't start loop: {e}", 'error')
			return False

	def move_loop(self):
		self.event_loop = True
		while self.event_loop is True:
			if self.key is None:
				pass
			elif self.key == 'stop' or self.key == 'Stop':
				log(f"PTZ EVENT: {self.key.lower()}", 'info')
				self.move(self.key.lower())
				self.key = None
			else:
				if self.key == 'arrow_up':
					self.servo = self.com['tilt']
					self.pos_y += self.step
					pos = self.pos_y
				elif self.key == 'arrow_down':
					self.servo = self.com['tilt']
					self.pos_y -= self.step
					pos = self.pos_y
				elif self.key == 'arrow_left':
					self.servo = self.com['pan']
					self.pos_x -= self.step
					pos = self.pos_x
				elif self.key == 'arrow_right':
					self.servo = self.com['pan']
					self.pos_x += self.step
					pos = self.pos_x
				log(f"PTZ EVENT: {self.key.lower()}", 'info')
				self.move(self.servo, pos)
				self.key = None
		
