import os


class message():
	def __init__(self):
		self.dest_id = 0
		self.pid = None
		self.camera_id = None
		self.priority = None
		self.name = __name__

	def new(self, camera_id, data, pid=None, dest_id=0, name=None, priority=5):
		if name is None:
			self.name = __name__
		self.dest_id = dest_id
		self.camera_id = camera_id
		self.data = data
		self.priority = priority
		self.name = name
		if pid is not None:
			self.pid = pid
		if self.pid is None:
			self.pid = os.getpid()
		return self

