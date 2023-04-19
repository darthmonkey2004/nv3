import time
import evdev
import subprocess
from log import nv_logger

log = nv_logger().log_msg



def get_keyboard():
	kbd = None
	com = f"sudo chmod a+rwx /dev/input/event*"
	ret = subprocess.check_output(com, shell=True).decode().strip()
	if ret != '':
		log(f"Error setting device permissions: {ret}", 'error')
		return None
	else:
		devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
		for dev in devices:
			if 'Keyboard' in dev.name:
				kbd = dev
				log(f"Grabbed keyboard:{dev.name} at path {dev.path}!", 'info')
				return kbd
	if kbd is None:
		log(f"Unable to grab keyboard! check permissions, and try again.", 'error')
		return kbd

class keyboard():
	def __init__(self):
		self.kbd = get_keyboard()
		self.last_len = 0
		self.len = 0
		self.active_keys = []
		self.last_key = None
		self.last_keys = self.active_keys

	def get_keys(self):
		self.last_keys = self.active_keys
		self.active_keys = self.kbd.active_keys()
		temp = []
		event = None
		if len(self.active_keys) > len(self.last_keys):
			event = 'KEY_DOWN'
			for k in self.active_keys:
				if k not in self.last_keys:
					out = (event, k)
					temp.append(out)
		elif len(self.active_keys) < len(self.last_keys):
			event = 'KEY_UP'
			for k in self.last_keys:
				if k not in self.active_keys:
					out = (event, k)
					temp.append(out)
		if temp == [] and event is None:
			return [(None, None)]
		else:
			return temp

if __name__ == "__main__":
	k = keyboard()
	while True:
		for event, code in k.get_keys():
			if event is not None:
				log(f"KEYBOARD EVENT: Event={event}, Code={code}", 'info')

