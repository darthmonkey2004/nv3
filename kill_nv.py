from os import kill
import psutil
from signal import SIGKILL
from log import nv_logger
log = nv_logger().log_msg


def get_pid():
	pid = None
	for proc in psutil.process_iter():
		if 'python3' in proc.name():
			for item in proc.cmdline():
				if 'start.py' in item:
					pid = proc.pid
	return pid


def kill_nv():
	try:
		pid = get_pid()
		if pid is not None:
			log(f"Killing nv at process id {pid}", 'info')
			kill(pid, SIGKILL)
			return True
		else:
			return False
	except Exception as e:
		log(f"Error killing process: {e}", 'error')
		return False
	
