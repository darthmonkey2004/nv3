from time import time
from kill_nv import *
from threading import Thread
#from nv.main.browser import *
import psutil
from conf import write_opts
import time
from ptz_control import ptz_control
from keyboard import keyboard
import PySimpleGUI as sg
from log import nv_logger
import sys
#import traceback
from keymap import ctk
from new_camera import *
from new_object import *
from settings_event_handler import event_mgr
log = nv_logger().log_msg

class nv_ui():
	def __init__(self, camera_id):
		self.event = None
		self.values = {}
		self.camera_id = camera_id
		self.opts = read_opts(self.camera_id)
		if self.opts['has_ptz']:
			self.ptz = ptz_control(self.camera_id)
		else:
			self.ptz = None
		self.location = self.opts['ptz']['window']['location']
		self.size = self.opts['ptz']['window']['size']
		self.settings_menus = ['PTZ Settings', 'Face Detection Settings', 'Object Detection Settings', 'Image Output Settings', 'Capture Settings', 'Server Settings', 'General Settings']
		self.keys = list(ctk.values())
		self.codes = list(ctk.keys())
		self.events = self.opts['ptz']['events']
		if self.ptz is not None:
			self.tour_wait_low = self.opts['ptz']['tour_wait_low']
			self.tour_wait_med = self.opts['ptz']['tour_wait_med']
			self.tour_wait_high = self.opts['ptz']['tour_wait_high']
			self.ptz_low = self.opts['ptz']['ptz_low']
			self.ptz_med = self.opts['ptz']['ptz_med']
			self.ptz_high = self.opts['ptz']['ptz_high']
			self.ptz_speed = self.opts['ptz']['ptz_speed']
			self.tour_wait = self.opts['ptz']['tour_wait']
			self.k = keyboard()
			self.keyboard_control = self.opts['ptz']['keyboard_control']
			self.keyboard_control = False
			if self.opts['ptz']['tour']:
				self.tour_started = None
				self.start_tour()
		self.exit = False
		self.active_windows = []
		self.settings_event_mgr = event_mgr
		self.preset = None
		self.tour_dest = 0
		self.titles = ['PTZ Settings', 'Face Detection Settings', 'Object Detection Settings', 'Image Output Settings', 'Capture Settings', 'Server Settings', 'General Settings']
		self.sections = ['ptz', 'face_detection', 'object_detection', 'image_output', 'capture', 'server', 'general', None]
		self.title = None
		self.win = self.ptz_ui()
		self.src_uri = None
		if self.ptz == None:
			self.ptz = ptz_control()
		if self.win == None:
			self.win = ptz_ui()
		self.ptz.set_speed(self.ptz_speed)
		self.run_tour = False

	def ptz_ui(self):
		layout = []
		menu_def = [['Settings', [self.settings_menus], 'Oak-D Lite']]
		menu = [sg.MenubarCustom(menu_def, tearoff=True, key='-menubar_key-')]
		add_camera = [sg.Input('', key='-ADD_CAMERA_URI-', enable_events=True, change_submits=True), sg.Button('Add Camera')]
		line1 = [sg.Button('Up Left'), sg.Button('Up'), sg.Button('Up Right')]
		line2 = [sg.Button('Left'), sg.Button('Stop'), sg.Button('Right')]
		line3 = [sg.Button('Down Left'), sg.Button('Down'), sg.Button('Down Right')]
		keyboard_checkbox = [sg.Button('Save Window Location'), sg.Checkbox('Keyboard Control:', default=False, enable_events=True, key='-KEYBOARD_CONTROL-'), sg.Checkbox('PTZ Auto Tracking:', default=self.opts['detector']['track_to_center'], enable_events=True, key='-PTZ_TRACKING-')]
		current_memory_box = [sg.Text(psutil.virtual_memory().percent, key='CURRENT_MEMORY')]
		layout.append(menu)
		layout.append(add_camera)
		layout.append(line1)
		layout.append(line2)
		layout.append(line3)
		layout.append(keyboard_checkbox)
		layout.append(current_memory_box)
		presets = []
		for i in range(0, 4):
			presets.append(i)
		preset_line = [sg.Text('Presets:'), sg.Combo(presets, 0, enable_events=True, key='-SELECT_PRESET-'), sg.Button('Set'), sg.Button('Goto')]
		layout.append(preset_line)
		last_line = [sg.Button('Tour Start'), sg.Button('Tour Stop'), sg.Button('Quit')]
		layout.append(last_line)
		self.win = sg.Window('PTZ Control', layout, return_keyboard_events=False, location=self.location, size=self.size, element_justification='center', finalize=True, resizable=True)
		return self.win

	def restore_default_settings(self, section='general'):
		o = init_opts(0)
		write_opts(o)
		self.log(f"Defaults restored!")
		return o


	def settings(section=None):
		if section is None:
			layout = []
			btn1 = [[sg.Button('General Settings')]]
			btn2 = [[sg.Button('Server Settings')]]
			btn3 = [[sg.Button('Capture Settings')]]
			btn4 = [[sg.Button('Image Output Settings')]]
			btn5 = [[sg.Button('Object Detection Settings')]]
			btn6 = [[sg.Button('Face Detection Settings')]]
			btn7 = [[sg.Button('PTZ Settings')]]
			layout.append(btn1)
			layout.append(btn2)
			layout.append(btn3)
			layout.append(btn4)
			layout.append(btn5)
			layout.append(btn6)
			layout.append(btn7)
			buttons = [[sg.Button('Close'), sg.Button('Save'), sg.Button('Restore Defaults')]]
			layout.append(buttons)
			win_main_settings = sg.Window("Settings Menu", layout=layout, auto_size_text=True, auto_size_buttons=True, location=(None, None), size=(None, None), icon=None, force_toplevel=False, return_keyboard_events=False, use_default_focus=True, keep_on_top=None, resizable=True, finalize=True, element_justification="center", enable_close_attempted_event=True)
			self.active_windows.append('Settings Menu')
			return win_main_settings
		elif section == 'General Settings':
			#-------------------------------------Frame General
			layout1 = []
			settings_debug_mode = [sg.Checkbox('Enable Debugging', default=self.opts['debug'], size=(None, None), auto_size_text=True, change_submits=True, enable_events=True, key='-DEBUG-')]
			layout1.append(settings_debug_mode)
			settings_win_w = [[sg.Text('Window Width:'), sg.Input(default_text=self.opts['ptz']['window']['size'][0], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-UI_WIDTH-', expand_x=True)]]
			settings_win_h = [[sg.Text('Window Height:'), sg.Input(default_text=self.opts['ptz']['window']['size'][1], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-UI_HEIGHT-', expand_x=True)]]
			settings_loc_x = [[sg.Text('Window Location (x):'), sg.Input(default_text=self.opts['ptz']['window']['location'][0], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-UI_LOC_X-', expand_x=True)]]
			settings_loc_y = [[sg.Text('Window Location (y):'), sg.Input(default_text=self.opts['ptz']['window']['location'][1], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-UI_LOC_Y-', expand_x=True)]]
			settings_dims = settings_win_w, settings_win_h
			settings_loc = settings_loc_x, settings_loc_y
			layout1.append(settings_dims)
			layout1.append(settings_loc)
			buttons = [[sg.Button('Close'), sg.Button('Save'), sg.Button('Restore Defaults')]]
			layout1.append(buttons)
			win1 = sg.Window("General Settings", layout=layout1, auto_size_text=True, auto_size_buttons=True, location=(None, None), size=(None, None), icon=None, force_toplevel=False, return_keyboard_events=False, use_default_focus=True, keep_on_top=None, resizable=True, finalize=True, element_justification="center", enable_close_attempted_event=True)
			self.active_windows.append('General Settings')
			return win1
		elif section == 'Server Settings':
			#------------------------------------Frame Server
			layout2 = []
			addr = self.opts['ptz']['addr']
			addresses = [addr, '127.0.0.1']
			settings_server_addr = [[sg.Text('Server Address:'), sg.Combo(addresses, default_value=addr, size=(None, None), auto_size_text=True, bind_return_key=True, change_submits=True, enable_events=True, key='-SERVER_ADDRESS-')]]
			settings_server_port = [[sg.Text('Server Port:'), sg.Input(default_text=self.opts['port'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-SERVER_PORT-', expand_x=True)]]
			layout2.append(settings_server_addr)
			layout2.append(settings_server_port)
			buttons = [[sg.Button('Close'), sg.Button('Save'), sg.Button('Restore Defaults')]]
			layout2.append(buttons)
			win2 = sg.Window("Server Settings", layout=layout2, auto_size_text=True, auto_size_buttons=True, location=(None, None), size=(None, None), icon=None, force_toplevel=False, return_keyboard_events=False, use_default_focus=True, keep_on_top=None, resizable=True, finalize=True, element_justification="center", enable_close_attempted_event=True)
			self.active_windows.append('Server Settings')
			return win2
		elif section == 'Capture Settings':
			#------------------------------------Frame Capture
			layout3 = []
			settings_camera_id = [[sg.Text('Camera ID:'), sg.Input(default_text="0", size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-CAMERA_ID-', expand_x=True)]]
			settings_camera_src = [[sg.Text('Source (url/device):'), sg.Input(default_text=self.opts[self.camera_id]['url'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-CAMERA_ID_SRC-', expand_x=True)]]
			settings_camera_h = [[sg.Text('Capture Height:'), sg.Input(default_text=self.opts[self.camera_id]['H'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-CAMERA_H-', expand_x=True)]]
			settings_camera_w = [[sg.Text('Capture Width:'), sg.Input(default_text=self.opts[self.camera_id]['W'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-CAMERA_W-', expand_x=True)]]
			line1 = [[settings_camera_id, settings_camera_h, settings_camera_w]]
			layout3.append(line1)
			layout3.append(settings_camera_src)
			camera_url = f"http://{self.opts['ptz']['addr']}:{self.opts['port']}/Camera_{self.opts['self.camera_id']}.mjpg"
			settings_camera_url = [[sg.Text('MJPG Url:'), sg.Input(default_text=camera_url, size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-CAMERA_URL-', expand_x=True)]]
			layout3.append(settings_camera_url)
			capture_methods = ['cv2', 'pil', 'raw', 'zmq', 'q']
			settings_capture_methods = [[sg.Text('Capture Methods:'), sg.Combo(capture_methods, default_value=self.opts['pull_method'], size=(None, None), auto_size_text=True, bind_return_key=True, change_submits=True, enable_events=True, key='-CAPTURE_METHOD-')]]
			settings_font = [[sg.Text('Font:'), sg.Input(default_text=self.opts['FONT'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-FONT-', expand_x=True)]]
			settings_font_scale = [[sg.Text('Font Scale:'), sg.Input(default_text=self.opts['FONT_SCALE'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-FONT_SCALE-', expand_x=True)]]
			line = settings_capture_methods, settings_font, settings_font_scale
			layout3.append(line)
			buttons = [[sg.Button('Close'), sg.Button('Save'), sg.Button('Restore Defaults')]]
			layout3.append(buttons)
			win3 = sg.Window("Capture Settings", layout=layout3, auto_size_text=True, auto_size_buttons=True, location=(None, None), size=(None, None), icon=None, force_toplevel=False, return_keyboard_events=False, use_default_focus=True, keep_on_top=None, resizable=True, finalize=True, element_justification="center", enable_close_attempted_event=True)
			self.active_windows.append('Capture Settings')
			return win3
		elif section == 'Image Output Settings':
			#---------------------------------------Image output frame
			layout4 = []
			settings_known_save_path = [[sg.Text('Path to known faces:'), sg.Input(default_text=self.opts['writeOutImg']['path']['known'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-IMG_KNOWN_SAVE_PATH-', expand_x=True)]]
			settings_unknown_save_path = [[sg.Text('Path to unknown faces:'), sg.Input(default_text=self.opts['writeOutImg']['path']['unknown'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-IMG_UNKNOWN_SAVE_PATH-', expand_x=True)]]
			settings_save_detected_images = [[sg.Text('Output images on detection:'), sg.Checkbox('Save Detections (Images)', default=self.opts['writeOutImg']['enabled'], size=(None, None), auto_size_text=True, change_submits=True, enable_events=True, key='-SAVE_OUTPUT_IMAGES-')]]
			layout4.append(settings_save_detected_images)
			layout4.append(settings_known_save_path)
			layout4.append(settings_unknown_save_path)
			buttons = [[sg.Button('Close'), sg.Button('Save'), sg.Button('Restore Defaults')]]
			layout4.append(buttons)
			win4 = sg.Window("Image Output Settings", layout=layout4, auto_size_text=True, auto_size_buttons=True, location=(None, None), size=(None, None), icon=None, force_toplevel=False, return_keyboard_events=False, use_default_focus=True, keep_on_top=None, resizable=True, finalize=True, element_justification="center", enable_close_attempted_event=True)
			self.active_windows.append('Image Output Settings')
			return win4
		elif section == 'Object Detection Settings':
			#---------------------------------------Facial and Detection Options
			##---------------------------------------Object Detection
			layout5 = []
			settings_set_det_provider = [[sg.Text('Detection Provider:'), sg.Combo(self.opts['detector']['all_providers'], default_value=self.opts['detector']['provider'], size=(None, None), auto_size_text=True, bind_return_key=True, change_submits=True, enable_events=True, key='-DETECTION_PROVIDER-')]]
			settings_set_det_methods = [[sg.Text('Detection Methods:'), sg.Listbox(self.opts['detector']['ALL_METHODS'], select_mode='multiple', change_submits=True, enable_events=True, size=(30, 5), auto_size_text=True, key='-ALL_DETECTION_METHODS-', expand_x=True, expand_y=False), sg.Listbox(self.opts['detector']['METHODS'], select_mode='multiple', change_submits=True, enable_events=True, size=(30, 5), auto_size_text=True, key='-ACTIVE_DETECTION_METHODS-', expand_x=True, expand_y=False), sg.Button('Add Method'), sg.Button('Remove Method')]]
			settings_set_det_prototxt = [[sg.Text('Path to prototxt:'), sg.Input(default_text=self.opts['detector']['object_detector']['prototxt'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-DETECTOR_PROTOTXT-', expand_x=True)]]
			settings_set_det_model = [[sg.Text('Path to model:'), sg.Input(default_text=self.opts['detector']['object_detector']['model'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-DETECTOR_MODEL-', expand_x=True)]]
			settings_set_det_targets = [[sg.Text('Target classes (filter):'), sg.Listbox(self.opts['detector']['object_detector']['classes'], default_values=self.opts['detector']['object_detector']['targets'], select_mode='multiple', change_submits=True, enable_events=True, size=(30, 5), auto_size_text=True, key='-ALL_DETECTION_TARGETS-', expand_x=False, expand_y=False), sg.Listbox(self.opts['detector']['object_detector']['targets'], select_mode='multiple', change_submits=True, enable_events=True, size=(30, 5), auto_size_text=True, key='-DETECTION_TARGETS-', expand_x=False, expand_y=False), sg.Button('Add Target'), sg.Button('Remove Target')]]
			settings_set_det_confidence = [[sg.Text('Detection confidence threshold:'), sg.Input(default_text=self.opts['detector']['object_detector']['confidence'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-DETECTOR_CONFIDENCE_THRESHOLD-', expand_x=True)]]
			line1 = settings_set_det_provider, settings_set_det_prototxt, settings_set_det_model, settings_set_det_confidence
			layout5.append(line1)
			layout5.append(settings_set_det_methods)
			layout5.append(settings_set_det_targets)
			buttons = [[sg.Button('Close'), sg.Button('Save'), sg.Button('Restore Defaults')]]
			layout5.append(buttons)
			win5 = sg.Window("Object Detection Settings", layout=layout5, auto_size_text=True, auto_size_buttons=True, location=(None, None), size=(None, None), icon=None, force_toplevel=False, return_keyboard_events=False, use_default_focus=True, keep_on_top=None, resizable=True, finalize=True, element_justification="center", enable_close_attempted_event=True)
			self.active_windows.append('Object Detection Settings')
			return win5
		elif section == 'Face Detection Settings':
			##---------------------------------------Face Detection
			layout6 = []
			fd_provider = f"fd_{self.opts['detector']['provider']}"
			fr_provider = f"fr_{self.opts['detector']['provider']}"
			settings_fd_cascade = [[sg.Text('Cascade file:'), sg.Input(default_text=self.opts['detector'][fd_provider]['face_cascade'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-FD_CASCADE_FILE-', expand_x=True)]]
			settings_scale_factor = [[sg.Text('Scale factor:'), sg.Input(default_text=self.opts['detector']['fd_cv2']['scale_factor'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-FD_SCALE_FACTOR-', expand_x=True)]]
			settings_minimum_neighbors = [[sg.Text('Minimum neighbors:'), sg.Input(default_text=self.opts['detector']['fd_cv2']['minimum_neighbors'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-FD_MINIMUM_NEIGHBORS-', expand_x=True)]]
			fr_dlib_models = ['hog', 'cnn']
			settings_fr_dlib_model = [[sg.Text('DLIB Detection Tolerance:'), sg.Input(default_text=self.opts['detector']['fr_dlib']['tolerance'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-FR_DLIB_TOLERANCE-', expand_x=True), sg.Text('DLIB Recognition Model:'), sg.Listbox(fr_dlib_models, default_values=self.opts['detector']['fr_dlib']['model'], select_mode='multiple', change_submits=True, enable_events=True, size=(None, None), auto_size_text=True, key='-FACE_RECOGNITION_MODELS-', expand_x=False, expand_y=False)]]
			settings_fr_cv2_dbpath = [[sg.Text('CV2 Saved Faces database:'), sg.Input(default_text=self.opts['detector']['fr_cv2']['dbpath'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-FR_CV2_DBPATH-', expand_x=True)]]
			settings_fr_dlib_passes = [[sg.Text('DLib recognizer passes (upsamples):'), sg.Input(default_text=self.opts['detector'][fd_provider]['face_cascade'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-FR_DLIB_PASSES-', expand_x=True)]]
			line = settings_scale_factor, settings_minimum_neighbors
			layout6.append(line)
			layout6.append(settings_fd_cascade)
			layout6.append(settings_fr_dlib_model)
			layout6.append(settings_fr_dlib_passes)
			layout6.append(settings_fr_cv2_dbpath)
			buttons = [[sg.Button('Close'), sg.Button('Save'), sg.Button('Restore Defaults')]]
			layout6.append(buttons)
			win6 = sg.Window("Face Detection Settings", layout=layout6, auto_size_text=True, auto_size_buttons=True, location=(None, None), size=(None, None), icon=None, force_toplevel=False, return_keyboard_events=False, use_default_focus=True, keep_on_top=None, resizable=True, finalize=True, element_justification="center", enable_close_attempted_event=True)
			self.active_windows.append('Face Detection Settings')
			return win6
		elif section == 'PTZ Settings':
		#---------------------------------------PTZ Controls
			layout7 = []
			settings_ptz_tour = [[sg.Text('Enable Tour:'), sg.Checkbox('Enable Tour', default=self.opts['ptz']['tour'], size=(None, None), auto_size_text=True, change_submits=True, enable_events=True, key='-TOUR-')]]
			settings_ptz_input_events = [[sg.Text('Enable Input Events:'), sg.Checkbox('Enable Input Events', default=self.opts['ptz']['events'], size=(None, None), auto_size_text=True, change_submits=True, enable_events=True, key='-ENABLE_EVENT_LOOP-')]]
			settings_tour_wait_low = [[sg.Text('Wait (low):'), sg.Input(default_text=self.opts['ptz']['tour_wait_low'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-TOUR_WAIT_LOW-', expand_x=True)]]
			settings_tour_wait_med = [[sg.Text('Wait (med):'), sg.Input(default_text=self.opts['ptz']['tour_wait_med'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-TOUR_WAIT_MED-', expand_x=True)]]
			settings_tour_wait_high = [[sg.Text('Wait (high):'), sg.Input(default_text=self.opts['ptz']['tour_wait_high'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-TOUR_WAIT_HIGH-', expand_x=True)]]
			ptz_speeds = ['0', '1', '2']
			settings_ptz_speeds = [[sg.Text('PTZ Speed:'), sg.Combo(ptz_speeds, default_value=self.opts['ptz']['ptz_speed'], size=(None, None), auto_size_text=True, bind_return_key=True, change_submits=True, enable_events=True, key='-PAN_SPEED-')]]
			line = settings_ptz_tour, settings_ptz_input_events, settings_ptz_speeds
			layout7.append(line)
			line = settings_tour_wait_low, settings_tour_wait_med, settings_tour_wait_high
			layout7.append(line)
			buttons = [[sg.Button('Close'), sg.Button('Save'), sg.Button('Restore Defaults')]]
			layout7.append(buttons)
			win7 = sg.Window("PTZ Settings", layout=layout7, auto_size_text=True, auto_size_buttons=True, location=(None, None), size=(None, None), icon=None, force_toplevel=False, return_keyboard_events=False, use_default_focus=True, keep_on_top=None, resizable=True, finalize=True, element_justification="center", enable_close_attempted_event=True)
			self.active_windows.append('PTZ Settings')
			return win7

	def quit(self):
		log(f"UI: Writing opts file (on exit)...", 'info')
		#send quit command to hub for propagation through the threads.
		write_opts(self.opts)
		kill_nv()
		exit()



	def keyboard(self):
		for event, code in self.k.get_keys():
			if event is not None:
				if event == 'KEY_UP':
					log(f"KEYBOARD: Event=Key Up, PTZ Stopped.", 'info')
					self.ptz.key = 'stop'
				elif event == 'KEY_DOWN':
					if code in self.codes:
						key = self.keys[self.codes.index(code)]
						if '_' in key:
							key = key.split('_')[1]
						self.ptz.key = key

	def tour(self):
		if self.tour_started is None:
			self.tour_started = time.time()
			self.tour_dest = 0
		else:
			duration = round(time.time() - self.tour_started)
			if duration >= self.tour_wait:
				if self.tour_dest == 0:
					self.tour_dest = 1
				elif self.tour_dest == 1:
					self.tour_dest = 0
				self.ptz.goto(self.tour_dest)
				self.tour_started = time.time()


	def read(self):
		if self.run_tour == True:
			self.tour()
		if self.keyboard_control == True:
			self.keyboard()
		win, event, values = sg.read_all_windows(timeout=1)
		if event == '__TIMEOUT__':
			return None, None, None
		else:
			return win, event, values
		

if __name__ == "__main__":
	import sys
	try:
		camera_id = int(sys.argv[1])
	except:
		log("No camera id given! Defaulting to 0...", 'warning')
		camera_id = 0

