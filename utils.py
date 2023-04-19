from log import nv_logger
import sys
import getpass
import keyring


logger = nv_logger().log_msg
RED = (255, 0, 0)
ORANGE = (255, 127.5, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 255)
INDIGO = (0, 0, 255)
VIOLET = (255, 0, 255)
COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE, INDIGO, VIOLET]


def log(msg, _type=None):
	if _type is None:
		_type = 'info'
	if _type == 'error':
		exc_info = sys.exc_info()
		logger(msg, _type, exc_info)
		return
	else:
		logger(msg, _type)


def set_auth(camera_id, pw):
	auth_key = f"Camera_{camera_id}:auth"
	try:
		keyring.set_password(auth_key, 'pw', pw)
		return auth_key
	except Exception as e:
		log(f"Failed to set password in keyring: {e}", 'error')
		return None


def get_auth(camera_id):
	auth_key = f"Camera_{camera_id}:auth"
	try:
		pw = keyring.get_password(auth_key, 'pw')
		if pw is not None:
			return pw
		else:
			log(f"Couldn't get password from store ({e})! Enter it now:", 'info')
			pw = getpass.getpass("Password: ")
			set_auth(camera_id, pw)
			log(f"Password stored in keyring!")
			return pw
	except Exception as e:
		log(f"Couldn't get password from store ({e})! Enter it now:", 'info')
		pw = getpass.getpass("Password: ")
		set_auth(camera_id, pw)
		log(f"Password stored in keyring!")
		return pw
