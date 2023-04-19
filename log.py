import sys, traceback
import pickle
import logging
import datetime
import os

DATA_DIR = os.path.join(os.path.expanduser("~"), '.np', 'nv')
LOGFILE = os.path.join(DATA_DIR, "nv.log")
CONFFILE = os.path.join(DATA_DIR, "nv.conf")


class nv_logger():
	def __init__(self):
		self.logfile = LOGFILE
		lvl_debug = getattr(logging, 'DEBUG', None)
		lvl_critical = getattr(logging, 'CRITICAL', None)
		lvl_error = getattr(logging, 'ERROR', None)
		lvl_fatal = getattr(logging, 'FATAL', None)
		lvl_fatal = getattr(logging, 'INFO', None)
		lvl_warning = getattr(logging, 'WARNING', None)
		self.debug = True
		self.log_type = 'debug'
		self.log_level = getattr(logging, self.log_type.upper(), None)
		logging.basicConfig(filename=self.logfile, level=self.log_level)
		self.msg = None
		self.thread_type = 'log'
		self.pid = os.getpid()

	def log_msg(self, *args):
		pos = -1
		t = datetime.datetime.now()
		ts = (str(t.day) + "-" + str(t.month) + "-" + str(t.year) + " " + str(t.hour) + ":" + str(t.minute) + ":" + str(t.second) + ":" + str(t.microsecond))
		for arg in args:
			pos = pos + 1
			if pos == 0:
				self.msg = (ts + "--" + str(arg))
			elif pos == 1:
				self.log_type = arg
				self.log_level = getattr(logging, self.log_type.upper(), None)
				logging.basicConfig(filename=self.logfile, level=self.log_level)
		

		if not isinstance(self.log_level, int):
			raise ValueError('Invalid log level: %s' % self.log_type)
			return
		if self.msg == None:
			raise ValueError(f'No message data provided!')
		if self.debug == True and self.log_level != 40:
			# if debug flag == True, override debug value and print all messages (unless error)
			self.log_level = 10
		if self.log_level == 10:#debug level
			logging.debug(self.msg)
			print(f"DEBUG::{self.msg}")
		elif self.log_level == 20:
			logging.info(self.msg)
		elif self.log_level == 30:
			logging.warning(self.msg)
		elif self.log_level == 40:
			try:
				formatted_lines = traceback.format_exc().splitlines()
				j = "\n"
				tb_text = j.join(formatted_lines)
				self.msg = (f"{ts}::{self.msg}\n{tb_text}")
			except Exception as e:
				print("tb_text", tb_text)
				self.msg = (f"{ts}::{self.msg}\nUnable to insert traceback info({e})")
			logging.error(self.msg)
			try:
				print(f"ERROR:{self.msg}")
			except Exception as e:
				ouch=("Unable to print error message, background process(?)", self.msg, e)
				logging.error(ouch)
				raise RuntimeError(ouch) from e
				print (f"Log class exiting with errors: {e}")
				return
		return
