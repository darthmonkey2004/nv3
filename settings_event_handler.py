from log import nv_logger
from conf import read_opts, write_opts
import sys

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

def save(opts):
	write_opts(opts)
	log(f"Options file written!", 'info')

def event_mgr(win, event, opts, values={}, camera_id=0):
	if event == 'Save':
		save(opts)
		log("Options updated!", 'info')
	elif event == 'Restore Defaults':
		opts = init_opts(camera_id)
		log("Default options restored!", 'info')
	elif event == '-DEBUG-':
		opts['debug'] = values[event]
		write_opts(opts)
		log(f"DEBUG setting updated! {opts['debug']}")
	elif event == '-UI_WIDTH-':
		w = values[event]
		h = win['-UI_HEIGHT-'].get()
		nw, nh = w, h
		opts['ptz']['window']['size'] = (nw, nh)
		log(f"Updated UI window width! ({nw}, {nh})")
	elif event == '-UI_HEIGHT-':
		h = values[event]
		w = win['-UI_WIDTH-'].get()
		nw, nh = w, h
		opts['ptz']['window']['size'] = (nw, nh)
		log(f"Updated UI window height! ({nw}, {nh})")
	elif event == '-UI_LOC_X-':
		x = values[event]
		ox, oy = opts['ptz']['window']['location']
		nx, ny = x, oy
		opts['ptz']['window']['location'] = (nx, ny)
		log(f"Updated UI window location(x)! ({nx}, {ny})")
	elif event == '-UI_LOC_Y-':
		y = values[event]
		ox, oy = opts['ptz']['window']['location']
		nx, ny = ox, y
		opts['ptz']['window']['location'] = (nx, ny)
		log(f"Updated UI window location(x)! ({nx}, {ny})")
	elif event == '-SERVER_ADDRESS-':
		opts['ptz']['addr'] = values[event]
		log(f"Update Server address!", 'info')
	elif event == '-SERVER_PORT-':
		opts['port'] = values[event]
		log(f"Update Server port!", 'info')
	elif event == '-CAMERA_ID-':
		camera_id = values[event]
		opts = read_opts(camera_id)
		log(f"Active camera changed! (ID: {camera_id})", 'info')
	elif event == '-CAMERA_H-':
		opts[camera_id]['H'] = values[event]
		log(f"Updated camera {camera_id} height!", 'info')
	elif event == '-CAMERA_W-':
		opts[camera_id]['W'] = values[event]
		log(f"Updated camera {camera_id} width!", 'info')
	elif event == '-CAMERA_ID_SRC-':
		opts[camera_id]['url'] = values[event]
		log(f"Updated camera source for id {camera_id}", 'info')
	elif event == '-CAMERA_URL-':
		opts['url'] = values[event]
		log(f"Updated mjpeg url for camera {camera_id}!", 'info')
	elif event == '-CAPTURE_METHOD-':
		opts['pull_method'] = values[event]
		log(f"Updated capture method! {values[event]}", 'info') 
	elif event == '-FONT-':
		opts['FONT'] = values[event]
		log(f"Updated font!", 'info')
	elif event == '-FONT_SCALE-':
		opts['FONT_SCALE'] = values[event]
		log(f"Updated font scale!", 'info')
	elif event == '-SAVE_OUTPUT_IMAGES-':
		opts['writeOutImg']['enabled'] = values[event]
		log(f"Updated output images ({values[event]})", 'info')
	elif event == '-IMG_KNOWN_SAVE_PATH-':
		opts['writeOutImg']['path']['known'] = values[event]
		log(f"Updated known faces save path! ({values[event]})", 'info')
	elif event == '-IMG_UNKNOWN_SAVE_PATH-':
		opts['writeOutImg']['path']['unknown'] = values[event]
		log(f"Updated unknown faces save path! ({values[event]})", 'info')
	elif event == 'Remove Method':
		rm = win['-ACTIVE_DETECTION_METHODS-'].get()
		methods = opts['detector']['METHODS']
		for m in rm:
			if m in methods:
				methods.remove(m)
		opts['detector']['METHODS'] = methods
		win['-ACTIVE_DETECTION_METHODS-'].update(opts['detector']['METHODS'])
		log(f"Updated active detection methods!", 'info')
	elif event == 'Add Method':
		add = win['-ALL_DETECTION_METHODS-'].get()
		methods = opts['detector']['METHODS']
		for m in add:
			if m not in methods:
				methods.append(m)
		opts['detector']['METHODS'] = methods
		win['-ACTIVE_DETECTION_METHODS-'].update(opts['detector']['METHODS'])
		log(f"Updated active detection methods!", 'info')
	elif event == 'Add Target':
		add = win['-ALL_DETECTION_TARGETS-'].get()
		targets = opts['detector']['object_detector']['targets']
		for t in add:
			if t not in targets:
				targets.append(t)
		opts['detector']['object_detector']['targets'] = targets
		win['-DETECTION_TARGETS-'].update(targets)
		log(f"Updated detection targets!", 'info')
	elif event == 'Remove Target':
		rm = win['-DETECTION_TARGETS-'].get()
		print("To remove: ", rm)
		targets = opts['detector']['object_detector']['targets']
		for t in rm:
			if t in targets:
				targets.remove(t)
		opts['detector']['object_detector']['targets'] = targets
		win['-DETECTION_TARGETS-'].update(targets)
		log(f"Updated detection targets!", 'info')
	elif event == '-DETECTION_PROVIDER-':
		opts['detector']['provider'] = values[event]
		log(f"Updated detection provider: {values[event]}", 'info')
	elif event == '-DETECTOR_PROTOTXT-':
		opts['detector']['object_detector']['prototxt'] = values[event]
		log(f"Updated object detector prototxt path! {values[event]}", 'info')
	elif event == '-DETECTOR_MODEL-':
		opts['detector']['object_detector']['model'] = values[event]
		log(f"Updated object detector prototxt path! {values[event]}", 'info')
	elif event == '-DETECTOR_CONFIDENCE_THRESHOLD-':
		opts['detector']['object_detector']['confidence'] = values[event]
		log(f"Updated object detector confidence threshold! {values[event]}", 'info')
	elif event == '-FD_SCALE_FACTOR-':
		p = opts['detector']['provider']
		key = f"fd_{p}"
		opts['detector'][key]['scale_factor'] = values[event]
		log("Updated {p} scale factor: {values[event]}", 'info')
	elif event == '-FD_MINIMUM_NEIGHBORS-':
		p = opts['detector']['provider']
		key = f"fd_{p}"
		opts['detector'][key]['minimum_neighbors'] = values[event]
		log("Updated {p} minimum neighbors (dimensional accuracy): {values[event]}", 'info')
	elif event == '-FD_CASCADE_FILE-':
		p = opts['detector']['provider']
		key = f"fd_{p}"
		opts['detector'][key]['face_cascade'] = values[event]
		log("Updated {p} haar cascade file: {values[event]}", 'info')
	elif event == '-FR_DLIB_PASSES-':
		opts['detector']['fr_dlib']['passes'] = values[event]
		log("Upsamples count set for dlib recognizer: {values[event]}", 'info')
	elif event == '-FR_DLIB_TOLERANCE-':
		opts['detector']['fr_dlib']['tolerance'] = values[event]
		log("Updated dlib recognition tolerance! {values[event]}", 'info')
	elif event == '-FACE_RECOGNITION_MODELS-':
		opts['detector']['fr_dlib']['model'] = values[event]
		log("Updated dlib recognition model! {values[event]}", 'info')
	elif event == '-FR_CV2_DBPATH-':
		opts['detector']['fr_cv2']['dbpath'] = values[event]
		log("Updated cv2 face recognition database path! {values[event]}", 'info')
	elif event == '-TOUR-':
		opts['ptz']['tour'] = values[event]
		log("Toggled auto tour value: {values[event]}", 'info')
	elif event == '-ENABLE_EVENT_LOOP-':
		opts['ptz']['event'] = values[event]
		log("Toggled event_loop in ptz controller: {values[event]}", 'info')
	elif event == '-PAN_SPEED-':
		val = values[event]
		if val == 0:
			opts['ptz']['tour_wait'] = opts['ptz']['tour_wait_high']
		elif val == 1:
			opts['ptz']['tour_wait'] = opts['ptz']['tour_wait_med']
		elif val == 2:
			opts['ptz']['tour_wait'] = opts['ptz']['tour_wait_low']
		opts['ptz']['ptz_speed'] = values[event]
		log("Pan/tilt speed (and tour pause values) updated: {values[event]}", 'info')
	elif event == '-TOUR_WAIT_LOW-':
		opts['ptz']['tour_wait_low'] = values[event]
		log("Tour low speed pause/wait time updated: {values[event]}", 'info')
	elif event == '-TOUR_WAIT_MED-':
		opts['ptz']['tour_wait_med'] = values[event]
		log("Tour medium speed pause/wait time updated: {values[event]}", 'info')
	elif event == '-TOUR_WAIT_HIGH-':
		opts['ptz']['tour_wait_hight'] = values[event]
		log("Tour high speed pause/wait time updated: {values[event]}", 'info')
	return opts
