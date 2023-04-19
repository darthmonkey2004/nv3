import subprocess
import sys
import PySimpleGUI as sg
from suntime import Sun, SunTimeException
import datetime
import os
import pickle
#import pathlib
from log import nv_logger
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

DATA_DIR = os.path.join(os.path.expanduser("~"), '.np', 'nv')
CONFFILE = os.path.join(DATA_DIR, 'nv.conf')
LOGFILE = os.path.join(DATA_DIR, 'nv.log')

def get_local_ip():
	com = "ip -o -4 a s | awk -F'[ /]+' '$2!~/lo/{print $4}' | grep \"192.168\""
	return subprocess.check_output(com, shell=True).decode().strip()

def get_user_input(window_title='User Input'):
	user_input = None
	input_box = sg.Input(default_text='', enable_events=True, change_submits=True, do_not_clear=True, key='-USER_INPUT-', expand_x=True)
	input_btn = sg.Button(button_text='Ok', auto_size_button=True, pad=(1, 1), key='-OK-')
	layout = [[input_box], [input_btn]]
	input_window = sg.Window(window_title, layout, keep_on_top=False, element_justification='center', finalize=True)
	while True:
		event, values = input_window.read()
		if event == sg.WIN_CLOSED:
			break
		elif event == '-OK-':
			input_window.close()
		elif event == '-USER_INPUT-':
			user_input = values[event]
	return user_input


def readConf(camera_id=None, path=None):
	if path == None:
		path = CONFFILE
	try:
		with open(path, 'rb') as f:
			cams = pickle.load(f)
		f.close()
		if camera_id is not None:
			return cams['cameras'][int(camera_id)]
		else:
			return cams
	except Exception as e:
		#log(f"Warning: conf file not found! Using defaults...", 'warning')
		camera_id = 0
		conf = {}
		conf['cameras'] = {}
		conf['cameras'][camera_id] = {}
		opts = init_opts(camera_id, _type='screen_grab')
		conf['cameras'][camera_id] = opts
		conf['debug'] = True
		with open(path, 'wb') as f:
			pickle.dump(conf, f)
		f.close()
		return conf

conf = readConf()

def writeConf(data):
	try:
		with open(CONFFILE, 'wb') as f:
			pickle.dump(data, f)
		f.close()
		
		log('conf.py, writeConf: Conf updated!', 'info')
		return True
	except Exception as e:
		print(f"Exception in conf.py, writeConf, line 83:{e}")
		return False



def init_opts(camera_id=None, src=None, ptz=None, _type=None, has_auth=None):
	if ptz is None:
		log(f"ptz not set! using None...", 'warning')
	if _type is None:
		_type = 'cv2'
	if src is None and _type != 'screen_grab':
		raise Exception(ValueError, 'Gonna need dat source uri!!! (currently None)')
	if has_auth is None:
		has_auth = False
	if camera_id is None:
		camera_id = 0
	data_dir = os.path.join(os.path.expanduser("~"), '.np', 'nv')
	conf = readConf()
	localip = get_local_ip()
	opts = {}
	opts['debug'] = True
	opts['maxsize'] = 30
	opts['display_method'] = 'local'
	opts['processing'] = True
	opts['detector'] = {}
	opts['detector']['track_to_center'] = False
	#opts['camera_id'] = camera_id
	opts['cameras'] = {}
	opts['cameras'][camera_id] = {}
	opts['confidence_filter'] = 0.5
	opts['writeOutImg'] = {}
	opts['writeOutImg']['path'] = {}
	opts['writeOutImg']['path']['known'] =  os.path.join(data_dir, 'Recognized Faces')
	opts['writeOutImg']['path']['unknown'] =  os.path.join(data_dir, 'Unrecognized Face')
	opts['writeOutImg']['enabled'] = True
	opts['skip_frames'] = 15
	opts['status'] = None
	opts['src'] = {}
	opts['src']['types'] = ['screen_grab', 'cv2', 'zmq']
	if _type is None:
		pos = -1
		for t in opts['src']['types']:
			pos += 1
			print(f"{pos}:{t}")
		opts['src']['type'] = opts['src']['types'][int(input("Enter a number: "))]
	else:
		opts['src']['type'] = _type
	if opts['src']['type'] == 'screen_grab':
		from mss import mss
		sct = mss()
		opts['src']['monitor'] = sct.monitors[len(sct.monitors) - 1]
	if src is None or src == '':
		opts['src']['url'] = None
	else:
		opts['src']['url'] = src
	if has_auth is None:
		has_auth = input("User and pass for this camera? (True/False)")
	try:
		opts['src']['has_auth'] = bool(has_auth)
	except:
		log(f"Input not understood ({has_auth}). Defaulting to False...", 'error')
		opts['src']['has_auth'] = False
	opts['src']['user'] = os.path.expanduser("~").split(f"{os.path.sep}home{os.path.sep}")[1]
	opts['H'] = 352
	opts['W'] = 640
	opts['has_ptz'] = False
	opts['detector']['METHODS'] = ['object_detection', 'face_recognition']
	opts['detector']['object_detector'] = {}
	opts['detector']['object_detector']['prototxt'] =  os.path.join(data_dir, 'MobileNetSSD_deploy.prototxt')
	opts['detector']['object_detector']['model'] =  os.path.join(data_dir, 'MobileNetSSD_deploy.caffemodel')
	opts['detector']['object_detector']['targets'] =  ['person', 'cat', 'horse', 'truck', 'dog', 'car', 'motorbike']
	opts['detector']['object_detector']['classes'] =  ['background', 'aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus', 'car', 'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse', 'motorbike', 'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tvmonitor']
	opts['detector']['object_detector']['confidence'] =  0.49
	opts['detector']['fd'] = {}
	opts['detector']['fr'] = {}
	opts['detector']['fr']['tolerance'] =  0.55
	opts['detector']['fr']['model'] =  'hog'
	opts['detector']['provider'] = 'dlib'
	opts['detector']['all_providers'] = ['cv2', 'dlib']
	opts['detector']['fr_cv2'] = {}
	opts['detector']['fr_cv2']['dbpath'] =  os.path.join(data_dir, 'cv2_fr_trained.yml')
	opts['detector']['fr_cv2']['face_cascade'] =  os.path.join(data_dir, 'haarcascade_frontalface_default.xml')
	opts['detector']['fr_cv2']['dataset'] = os.path.join(os.path.expanduser("~"), '.np', 'nv', 'dataset')
	opts['detector']['fr_dlib'] = {}
	opts['detector']['fr_dlib']['tolerance'] =  0.55
	opts['detector']['fr_dlib']['model'] =  'hog'
	opts['detector']['fr_dlib']['upsamples'] = 1
	opts['detector']['fr_dlib']['type'] = 'large'
	opts['detector']['fr_dlib']['passes'] = 1
	opts['detector']['fd_cv2'] = {}
	opts['detector']['fd_cv2']['scale_factor'] =  1.1
	opts['detector']['fd_cv2']['minimum_neighbors'] =  5
	opts['detector']['fd_cv2']['face_cascade'] =  os.path.join(data_dir, 'haarcascade_frontalface_default.xml')
	opts['detector']['fd_dlib'] = {}
	opts['detector']['fd_dlib']['face_cascade'] =  os.path.join(data_dir, 'haarcascade_frontalface_default.xml')
	opts['detector']['ALL_METHODS'] = ['object_detection', 'face_detection', 'yolov3', 'face_recognition']
	opts['detector']['scraper'] = {}
	opts['detector']['scraper']['path_out'] = os.path.join(data_dir, 'scraped_dataset')
	opts['port'] = 8080
	opts['addr'] = localip
	opts['url'] = f"http://{localip}:{opts['port']}/Camera_{camera_id}.mjpg"
	opts['addr'] = localip
	opts['pull_method'] = 'q'
	opts['FONT'] = 0
	opts['FONT_SCALE'] = 1
	opts['ptz'] = {}
	if ptz is True:
		opts['ptz']['addr'] = opts['src']['url'].split('://')[1].split('/')[0]
	else:
		opts['ptz']['addr'] = None
	opts['ptz']['events'] = True
	opts['ptz']['tour_wait_low'] = 15
	opts['ptz']['tour_wait_med'] = 10
	opts['ptz']['tour_wait_high'] = 7
	opts['ptz']['ptz_low'] = 2
	opts['ptz']['ptz_med'] = 1
	opts['ptz']['ptz_high'] = 0
	opts['ptz']['ptz_speed'] = 1
	opts['ptz']['tour_wait'] = 10
	opts['ptz']['keyboard_control'] = False
	opts['ptz']['tour'] = False
	opts['ptz']['base_path'] = 'web/cgi-bin/hi3510'
	opts['ptz']['control_endpoint'] = 'ptzctrl.cgi'
	opts['ptz']['param_endpoint'] = 'param.cgi'
	opts['ptz']['window'] = {}
	opts['ptz']['window']['location'] =  (20, 1220)
	opts['ptz']['window']['size'] =  (400, 400)
	opts['ptz']['auth'] = {}
	opts['ptz']['auth']['uses_auth'] = True
	opts['ptz']['auth']['user'] = os.path.expanduser("~").split(f"{os.path.sep}home{os.path.sep}")[1]
	opts['tracker'] = {}
	opts['tracker']['types'] = {}
	opts['tracker']['types']['available'] = ['BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'MOSSE', 'CSRT']
	opts['tracker']['types']['selected'] = 'CSRT'
	opts['tracker']['max_age'] = 300
	return opts

def init_camera(camera_id, src, ptz=None, _type=None, has_auth=None):
	conf = readConf()
	if camera_id not in list(conf['cameras'].keys()):
		conf['cameras'][camera_id] = init_opts(camera_id=camera_id, src=src, ptz=ptz, _type=_type, has_auth=has_auth)
		log(f"Camera {camera_id} initialized!", 'info')
		writeConf(conf)
	else:
		log(f"Camera id already exists: {camera_id}", 'warning')
	return conf['cameras'][camera_id]

def write_opts(opts, camera_id=None):
	# update options config for camera id
	conf = readConf()
	try:
		if camera_id is None:
			camera_id = opts['camera_id']
		conf['cameras'][camera_id] = opts
		writeConf(conf)
		return True
	except Exception as e:
		log(f"Unable to write options to config file: {e}", 'error')
		return False


def read_opts(camera_id=None):
	if type(camera_id) != int:
		txt = f"conf.read_opts:camera_id:{camera_id}"
		raise Exception(TypeError, txt)
	conf = readConf()
	if camera_id is None:
		camera_id = 0
	#try:
	if camera_id in list(conf['cameras'].keys()):
		return conf['cameras'][camera_id]
	else:
		log(f"conf.read_opts:Camera id ({camera_id}) not found! Initializing  from default...", 'warning')
		src = input("Enter source uri: ")
		conf['cameras'][camera_id] = init_opts(camera_id=camera_id, src=src, ptz=None, _type=None, has_auth=None)


def get_local_ip():
	lines = subprocess.check_output('ifconfig', shell=True).decode().strip().split("\n")
	for line in lines:
		if '192.168.' in line:
			return line.split('inet ')[1].split(' ')[0]

def init_conf(camera_id=None):
	if camera_id is None:
		conf = readConf()
		keys = list(conf['cameras'].keys())
		camera_id = len(keys)
	nvdir = os.path.join(os.path.expanduser("~"), '.np', 'nv')
	conf = readConf(camera_id)
	conf['cameras'][camera_id] = {}
	d = conf['cameras'][camera_id]
	d['confidence_filter'] = 0.5
	d['writeOutImg'] = {}
	d['path'] = {}
	d['path']['known'] = os.path.join(nvdir, 'Recognized Faces')
	d['path']['unknown'] = os.path.join(nvdir, 'Unrecognized Face')
	d['enabled'] = False
	d['skip_frames'] = 15
	d['status'] = None
	d['src'] = {}
	d['src']['url'] = None
	d['src']['has_auth'] = False
	user = os.path.expanduser("~").split('/home/')[1]
	d['src']['user'] = user
	d['src']['url'] = input("Enter camera source uri: ")
	d['port'] = input("please choose a streaming port: ")
	d['types'] = ['screen_grab', 'cv2', 'zmq']
	d['type'] = 'cv2'
	d['H'] = 352
	d['W'] = 640
	d['has_ptz'] = False
	d['detector'] = {}
	d['detector']['METHODS'] = ['object_detection']
	d['detector']['object_detector'] = {}
	d['detector']['object_detector']['prototxt'] = os.path.join(nvdir, 'MobileNetSSD_deploy.prototxt')
	d['detector']['object_detector']['model'] = os.path.join(nvdir, 'MobileNetSSD_deploy.caffemodel')
	d['detector']['object_detector']['targets'] = ['person', 'cat', 'horse', 'truck', 'dog', 'car', 'motorbike']
	d['detector']['object_detector']['classes'] = ['background', 'aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus', 'car', 'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse', 'motorbike', 'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tvmonitor']
	d['detector']['object_detector']['confidence'] = 0.92
	d['detector']['fd'] = {}
	d['detector']['fr'] = {}
	d['detector']['fr']['tolerance'] = 0.55
	d['detector']['fr']['model'] = 'hog'
	d['detector']['fr']['provider'] = 'cv2'
	d['detector']['fr']['all_providers'] = ['cv2', 'dlib']
	d['detector']['fr_cv2'] = {}
	d['detector']['fr_cv2']['dbpath'] = os.path.join(nvdir, 'cv2_fr_trained.yml')
	d['detector']['fr_cv2']['face_cascade'] = os.path.join(nvdir, 'haarcascade_frontalface_default.xml')
	d['detector']['fr_cv2']['dataset'] = os.path.join(nvdir, 'dataset')
	d['detector']['fr_dlib'] = {}
	d['detector']['fr_dlib']['tolerance'] = 0.55
	d['detector']['fr_dlib']['model'] = 'hog'
	d['detector']['fr_dlib']['upsamples'] = 1
	d['detector']['fr_dlib']['type'] = 'large'
	d['detector']['fr_dlib']['passes'] = 1
	d['detector']['fd_cv2'] = {}
	d['detector']['fd_cv2']['scale_factor'] = 1.1
	d['detector']['fd_cv2']['minimum_neighbors'] = 5
	d['detector']['fd_cv2']['face_cascade'] = os.path.join(nvdir, 'haarcascade_frontalface_default.xml')
	d['detector']['fd_dlib'] = {}
	d['detector']['fd_dlib']['face_cascade'] = os.path.join(nvdir, 'haarcascade_frontalface_default.xml')
	d['detector']['ALL_METHODS'] = ['object_detection', 'face_detection', 'yolov3', 'face_recognition']
	d['detector']['scraper'] = {}
	d['detector']['scraper']['path_out'] = os.path.join(nvdir, 'scraped_dataset')
	d['detector']['track_to_center'] = False
	d['port'] = None
	d['addr'] = get_local_ip()
	d['url'] = None
	d['pull_method'] = 'q'
	d['FONT'] = 0
	d['FONT_SCALE'] = 1
	d['ptz'] = {}
	d['ptz']['addr'] = None
	d['ptz']['events'] = False
	d['ptz']['tour_wait_low'] = 15
	d['ptz']['tour_wait_med'] = 10
	d['ptz']['tour_wait_high'] = 7
	d['ptz']['ptz_low'] = 2
	d['ptz']['ptz_med'] = 1
	d['ptz']['ptz_high'] = 0
	d['ptz']['ptz_speed'] = '0'
	d['ptz']['tour_wait'] = 10
	d['ptz']['keyboard_control'] = False
	d['ptz']['tour'] = False
	d['ptz']['base_path'] = 'web/cgi-bin/hi3510'
	d['ptz']['control_endpoint'] = 'ptzctrl.cgi'
	d['ptz']['param_endpoint'] = 'param.cgi'
	d['ptz']['window'] = {}
	d['ptz']['window']['location'] = (20, 1220)
	d['ptz']['window']['size'] = (400, 400)
	d['ptz']['uses_auth'] = False
	d['ptz']['user'] = user
	d['ptz']['track_on_center'] = False
	d['method'] = 'q'
	d['maxsize'] = 30
	d['display_method'] = 'local'
	d['tracker'] = {}
	d['tracker']['types'] = {}
	d['tracker']['types']['available'] = ['BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'MOSSE', 'CSRT']
	d['tracker']['types']['selected'] = 'CSRT'
	d['tracker']['max_age'] = 100
	d['tracker']['max_misses'] = 50
	d['testsettings'] = {}
	d['testsettings']['size'] = (1112, 441)
	d['testsettings']['location'] = (320, 1839)
	d['processing'] = True
	d['url'] = f"http://{d['addr']}:{d['port']}/Camera_{camera_id}.mjpg"
	d['ptz']['addr'] = d['addr']
	return d


