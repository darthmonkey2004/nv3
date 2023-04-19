import sys, traceback
import PySimpleGUI as sg
from conf import read_opts, init_opts, write_opts
import subprocess
from log import nv_logger
from settings_event_handler import event_mgr
active_windows = []
camera_id = 0
opts = read_opts(camera_id)
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


def restore_defaults(section='general'):
	o = init_opts(0)
	write_opts(o)
	log(f"Defaults restored!")
	return o


def settings(section=None):
	global active_windows
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
		active_windows.append('Settings Menu')
		return win_main_settings
	elif section == 'General Settings':
		#-------------------------------------Frame General
		layout1 = []
		settings_debug_mode = [sg.Checkbox('Enable Debugging', default=opts['debug'], size=(None, None), auto_size_text=True, change_submits=True, enable_events=True, key='-DEBUG-')]
		layout1.append(settings_debug_mode)
		settings_win_w = [[sg.Text('Window Width:'), sg.Input(default_text=opts['ptz']['window']['size'][0], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-UI_WIDTH-', expand_x=True)]]
		settings_win_h = [[sg.Text('Window Height:'), sg.Input(default_text=opts['ptz']['window']['size'][1], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-UI_HEIGHT-', expand_x=True)]]
		settings_loc_x = [[sg.Text('Window Location (x):'), sg.Input(default_text=opts['ptz']['window']['location'][0], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-UI_LOC_X-', expand_x=True)]]
		settings_loc_y = [[sg.Text('Window Location (y):'), sg.Input(default_text=opts['ptz']['window']['location'][1], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-UI_LOC_Y-', expand_x=True)]]
		settings_dims = settings_win_w, settings_win_h
		settings_loc = settings_loc_x, settings_loc_y
		layout1.append(settings_dims)
		layout1.append(settings_loc)
		buttons = [[sg.Button('Close'), sg.Button('Save'), sg.Button('Restore Defaults')]]
		layout1.append(buttons)
		win1 = sg.Window("General Settings", layout=layout1, auto_size_text=True, auto_size_buttons=True, location=(None, None), size=(None, None), icon=None, force_toplevel=False, return_keyboard_events=False, use_default_focus=True, keep_on_top=None, resizable=True, finalize=True, element_justification="center", enable_close_attempted_event=True)
		active_windows.append('General Settings')
		return win1
	elif section == 'Server Settings':
		#------------------------------------Frame Server
		layout2 = []
		addr = opts['ptz']['addr']
		addresses = [addr, '127.0.0.1']
		settings_server_addr = [[sg.Text('Server Address:'), sg.Combo(addresses, default_value=addr, size=(None, None), auto_size_text=True, bind_return_key=True, change_submits=True, enable_events=True, key='-SERVER_ADDRESS-')]]
		settings_server_port = [[sg.Text('Server Port:'), sg.Input(default_text=opts['port'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-SERVER_PORT-', expand_x=True)]]
		layout2.append(settings_server_addr)
		layout2.append(settings_server_port)
		buttons = [[sg.Button('Close'), sg.Button('Save'), sg.Button('Restore Defaults')]]
		layout2.append(buttons)
		win2 = sg.Window("Server Settings", layout=layout2, auto_size_text=True, auto_size_buttons=True, location=(None, None), size=(None, None), icon=None, force_toplevel=False, return_keyboard_events=False, use_default_focus=True, keep_on_top=None, resizable=True, finalize=True, element_justification="center", enable_close_attempted_event=True)
		active_windows.append('Server Settings')
		return win2
	elif section == 'Capture Settings':
		#------------------------------------Frame Capture
		layout3 = []
		settings_camera_id = [[sg.Text('Camera ID:'), sg.Input(default_text="0", size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-CAMERA_ID-', expand_x=True)]]
		settings_camera_src = [[sg.Text('Source (url/device):'), sg.Input(default_text=opts[camera_id]['url'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-CAMERA_ID_SRC-', expand_x=True)]]
		settings_camera_h = [[sg.Text('Capture Height:'), sg.Input(default_text=opts[camera_id]['H'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-CAMERA_H-', expand_x=True)]]
		settings_camera_w = [[sg.Text('Capture Width:'), sg.Input(default_text=opts[camera_id]['W'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-CAMERA_W-', expand_x=True)]]
		line1 = [[settings_camera_id, settings_camera_h, settings_camera_w]]
		layout3.append(line1)
		layout3.append(settings_camera_src)
		camera_url = f"http://{opts['ptz']['addr']}:{opts['port']}/Camera_{opts['camera_id']}.mjpg"
		settings_camera_url = [[sg.Text('MJPG Url:'), sg.Input(default_text=camera_url, size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-CAMERA_URL-', expand_x=True)]]
		layout3.append(settings_camera_url)
		capture_methods = ['cv2', 'pil', 'raw', 'zmq', 'q']
		settings_capture_methods = [[sg.Text('Capture Methods:'), sg.Combo(capture_methods, default_value=opts['pull_method'], size=(None, None), auto_size_text=True, bind_return_key=True, change_submits=True, enable_events=True, key='-CAPTURE_METHOD-')]]
		settings_font = [[sg.Text('Font:'), sg.Input(default_text=opts['FONT'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-FONT-', expand_x=True)]]
		settings_font_scale = [[sg.Text('Font Scale:'), sg.Input(default_text=opts['FONT_SCALE'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-FONT_SCALE-', expand_x=True)]]
		line = settings_capture_methods, settings_font, settings_font_scale
		layout3.append(line)
		buttons = [[sg.Button('Close'), sg.Button('Save'), sg.Button('Restore Defaults')]]
		layout3.append(buttons)
		win3 = sg.Window("Capture Settings", layout=layout3, auto_size_text=True, auto_size_buttons=True, location=(None, None), size=(None, None), icon=None, force_toplevel=False, return_keyboard_events=False, use_default_focus=True, keep_on_top=None, resizable=True, finalize=True, element_justification="center", enable_close_attempted_event=True)
		active_windows.append('Capture Settings')
		return win3
	elif section == 'Image Output Settings':
		#---------------------------------------Image output frame
		layout4 = []
		settings_known_save_path = [[sg.Text('Path to known faces:'), sg.Input(default_text=opts['writeOutImg']['path']['known'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-IMG_KNOWN_SAVE_PATH-', expand_x=True)]]
		settings_unknown_save_path = [[sg.Text('Path to unknown faces:'), sg.Input(default_text=opts['writeOutImg']['path']['unknown'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-IMG_UNKNOWN_SAVE_PATH-', expand_x=True)]]
		settings_save_detected_images = [[sg.Text('Output images on detection:'), sg.Checkbox('Save Detections (Images)', default=opts['writeOutImg']['enabled'], size=(None, None), auto_size_text=True, change_submits=True, enable_events=True, key='-SAVE_OUTPUT_IMAGES-')]]
		layout4.append(settings_save_detected_images)
		layout4.append(settings_known_save_path)
		layout4.append(settings_unknown_save_path)
		buttons = [[sg.Button('Close'), sg.Button('Save'), sg.Button('Restore Defaults')]]
		layout4.append(buttons)
		win4 = sg.Window("Image Output Settings", layout=layout4, auto_size_text=True, auto_size_buttons=True, location=(None, None), size=(None, None), icon=None, force_toplevel=False, return_keyboard_events=False, use_default_focus=True, keep_on_top=None, resizable=True, finalize=True, element_justification="center", enable_close_attempted_event=True)
		active_windows.append('Image Output Settings')
		return win4
	elif section == 'Object Detection Settings':
		#---------------------------------------Facial and Detection Options
		##---------------------------------------Object Detection
		layout5 = []
		settings_set_det_provider = [[sg.Text('Detection Provider:'), sg.Combo(opts['detector']['all_providers'], default_value=opts['detector']['provider'], size=(None, None), auto_size_text=True, bind_return_key=True, change_submits=True, enable_events=True, key='-DETECTION_PROVIDER-')]]
		settings_set_det_methods = [[sg.Text('Detection Methods:'), sg.Listbox(opts['detector']['ALL_METHODS'], select_mode='multiple', change_submits=True, enable_events=True, size=(30, 5), auto_size_text=True, key='-ALL_DETECTION_METHODS-', expand_x=True, expand_y=False), sg.Listbox(opts['detector']['METHODS'], select_mode='multiple', change_submits=True, enable_events=True, size=(30, 5), auto_size_text=True, key='-ACTIVE_DETECTION_METHODS-', expand_x=True, expand_y=False), sg.Button('Add Method'), sg.Button('Remove Method')]]
		settings_set_det_prototxt = [[sg.Text('Path to prototxt:'), sg.Input(default_text=opts['detector']['object_detector']['prototxt'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-DETECTOR_PROTOTXT-', expand_x=True)]]
		settings_set_det_model = [[sg.Text('Path to model:'), sg.Input(default_text=opts['detector']['object_detector']['model'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-DETECTOR_MODEL-', expand_x=True)]]
		settings_set_det_targets = [[sg.Text('Target classes (filter):'), sg.Listbox(opts['detector']['object_detector']['classes'], default_values=opts['detector']['object_detector']['targets'], select_mode='multiple', change_submits=True, enable_events=True, size=(30, 5), auto_size_text=True, key='-ALL_DETECTION_TARGETS-', expand_x=False, expand_y=False), sg.Listbox(opts['detector']['object_detector']['targets'], select_mode='multiple', change_submits=True, enable_events=True, size=(30, 5), auto_size_text=True, key='-DETECTION_TARGETS-', expand_x=False, expand_y=False), sg.Button('Add Target'), sg.Button('Remove Target')]]
		settings_set_det_confidence = [[sg.Text('Detection confidence threshold:'), sg.Input(default_text=opts['detector']['object_detector']['confidence'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-DETECTOR_CONFIDENCE_THRESHOLD-', expand_x=True)]]
		line1 = settings_set_det_provider, settings_set_det_prototxt, settings_set_det_model, settings_set_det_confidence
		layout5.append(line1)
		layout5.append(settings_set_det_methods)
		layout5.append(settings_set_det_targets)
		buttons = [[sg.Button('Close'), sg.Button('Save'), sg.Button('Restore Defaults')]]
		layout5.append(buttons)
		win5 = sg.Window("Object Detection Settings", layout=layout5, auto_size_text=True, auto_size_buttons=True, location=(None, None), size=(None, None), icon=None, force_toplevel=False, return_keyboard_events=False, use_default_focus=True, keep_on_top=None, resizable=True, finalize=True, element_justification="center", enable_close_attempted_event=True)
		active_windows.append('Object Detection Settings')
		return win5
	elif section == 'Face Detection Settings':
		##---------------------------------------Face Detection
		layout6 = []
		fd_provider = f"fd_{opts['detector']['provider']}"
		fr_provider = f"fr_{opts['detector']['provider']}"
		settings_fd_cascade = [[sg.Text('Cascade file:'), sg.Input(default_text=opts['detector'][fd_provider]['face_cascade'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-FD_CASCADE_FILE-', expand_x=True)]]
		settings_scale_factor = [[sg.Text('Scale factor:'), sg.Input(default_text=opts['detector']['fd_cv2']['scale_factor'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-FD_SCALE_FACTOR-', expand_x=True)]]
		settings_minimum_neighbors = [[sg.Text('Minimum neighbors:'), sg.Input(default_text=opts['detector']['fd_cv2']['minimum_neighbors'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-FD_MINIMUM_NEIGHBORS-', expand_x=True)]]
		fr_dlib_models = ['hog', 'cnn']
		settings_fr_dlib_model = [[sg.Text('DLIB Detection Tolerance:'), sg.Input(default_text=opts['detector']['fr_dlib']['tolerance'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-FR_DLIB_TOLERANCE-', expand_x=True), sg.Text('DLIB Recognition Model:'), sg.Listbox(fr_dlib_models, default_values=opts['detector']['fr_dlib']['model'], select_mode='multiple', change_submits=True, enable_events=True, size=(None, None), auto_size_text=True, key='-FACE_RECOGNITION_MODELS-', expand_x=False, expand_y=False)]]
		settings_fr_cv2_dbpath = [[sg.Text('CV2 Saved Faces database:'), sg.Input(default_text=opts['detector']['fr_cv2']['dbpath'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-FR_CV2_DBPATH-', expand_x=True)]]
		settings_fr_dlib_passes = [[sg.Text('DLib recognizer passes (upsamples):'), sg.Input(default_text=opts['detector'][fd_provider]['face_cascade'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-FR_DLIB_PASSES-', expand_x=True)]]
		line = settings_scale_factor, settings_minimum_neighbors
		layout6.append(line)
		layout6.append(settings_fd_cascade)
		layout6.append(settings_fr_dlib_model)
		layout6.append(settings_fr_dlib_passes)
		layout6.append(settings_fr_cv2_dbpath)
		buttons = [[sg.Button('Close'), sg.Button('Save'), sg.Button('Restore Defaults')]]
		layout6.append(buttons)
		win6 = sg.Window("Face Detection Settings", layout=layout6, auto_size_text=True, auto_size_buttons=True, location=(None, None), size=(None, None), icon=None, force_toplevel=False, return_keyboard_events=False, use_default_focus=True, keep_on_top=None, resizable=True, finalize=True, element_justification="center", enable_close_attempted_event=True)
		active_windows.append('Face Detection Settings')
		return win6
	elif section == 'PTZ Settings':
	#---------------------------------------PTZ Controls
		layout7 = []
		settings_ptz_tour = [[sg.Text('Enable Tour:'), sg.Checkbox('Enable Tour', default=opts['ptz']['tour'], size=(None, None), auto_size_text=True, change_submits=True, enable_events=True, key='-TOUR-')]]
		settings_ptz_input_events = [[sg.Text('Enable Input Events:'), sg.Checkbox('Enable Input Events', default=opts['ptz']['events'], size=(None, None), auto_size_text=True, change_submits=True, enable_events=True, key='-ENABLE_EVENT_LOOP-')]]
		settings_tour_wait_low = [[sg.Text('Wait (low):'), sg.Input(default_text=opts['ptz']['tour_wait_low'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-TOUR_WAIT_LOW-', expand_x=True)]]
		settings_tour_wait_med = [[sg.Text('Wait (med):'), sg.Input(default_text=opts['ptz']['tour_wait_med'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-TOUR_WAIT_MED-', expand_x=True)]]
		settings_tour_wait_high = [[sg.Text('Wait (high):'), sg.Input(default_text=opts['ptz']['tour_wait_high'], size=(None, None), change_submits=True, enable_events=True, do_not_clear=True, key='-TOUR_WAIT_HIGH-', expand_x=True)]]
		ptz_speeds = ['0', '1', '2']
		settings_ptz_speeds = [[sg.Text('PTZ Speed:'), sg.Combo(ptz_speeds, default_value=opts['ptz']['ptz_speed'], size=(None, None), auto_size_text=True, bind_return_key=True, change_submits=True, enable_events=True, key='-PAN_SPEED-')]]
		line = settings_ptz_tour, settings_ptz_input_events, settings_ptz_speeds
		layout7.append(line)
		line = settings_tour_wait_low, settings_tour_wait_med, settings_tour_wait_high
		layout7.append(line)
		buttons = [[sg.Button('Close'), sg.Button('Save'), sg.Button('Restore Defaults')]]
		layout7.append(buttons)
		win7 = sg.Window("PTZ Settings", layout=layout7, auto_size_text=True, auto_size_buttons=True, location=(None, None), size=(None, None), icon=None, force_toplevel=False, return_keyboard_events=False, use_default_focus=True, keep_on_top=None, resizable=True, finalize=True, element_justification="center", enable_close_attempted_event=True)
		active_windows.append('PTZ Settings')
		return win7

def quit(opts):
	log(f"UI: Writing opts file (on exit)...", 'info')
	write_opts(opts)

def event_loop():
	global active_windows, opts
	titles = ['PTZ Settings', 'Face Detection Settings', 'Object Detection Settings', 'Image Output Settings', 'Capture Settings', 'Server Settings', 'General Settings']
	sections = ['ptz', 'face_detection', 'object_detection', 'image_output', 'capture', 'server', 'general', None]
	exit = False
	title = None
	while True:
		if exit == True:
			quit(opts)
			break
		try:
			window, event, values = sg.read_all_windows(timeout=1)
		except Exception as e:
			log(f"Exit exception:{e}", 'error')
			exit = True
		if event == '__TIMEOUT__':
			pass
		else:
			print(event, active_windows)
			if opts['debug'] == True:
				log(f"EVENT: {event}", 'info')
				
			if event in titles:
				if event in active_windows:
					log(f"WARNING: Window already open! Skipping...", 'warning')
				else:
					win = settings(event)
					#active_windows.append(event)
			elif event == sg.WIN_CLOSED or event == 'Close':
				title = window.Title
				window.close()
				if title in active_windows:
					active_windows.remove(title)
				else:
					log(f"Error: Window already closed!", 'error')
				if len(active_windows) == 0:
					log(f"All windows closed! Exiting...", 'info')
					exit = True
			else:
				opts = event_mgr(window, event, opts, values)
				

if __name__ == "__main__":
	import sys
	try:
		section = sys.argv[1]
	except:
		section = 'general'
	win = settings(section)
	event_loop()
