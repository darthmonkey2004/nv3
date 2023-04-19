from utils import get_auth, set_auth
import os
import subprocess
import PySimpleGUI as sg
import keyring
from log import nv_logger
import sys
from conf import *

exit_loop = False


log = nv_logger().log_msg


def get_new_id():
	path = os.path.join(os.path.expanduser("~"), '.np', 'nv')
	pos = 0
	for filepath in list(os.walk(path)):
		if 'ptz_opts_' in filepath and '.conf' in filepath:
			pos += 1
	return pos + 1

def new_camera(camera_id=None, src=None):
	user = os.path.expanduser("~").split('/home/')[1]
	if camera_id is None:
		camera_id = int(get_new_id())
	print(f"running menu! camera_id:{camera_id}, src:{src}")
	opts = init_opts(camera_id, ptz='n', src=src, _type='cv2', has_auth=False)
	location = opts['ptz']['window']['location']
	size = opts['ptz']['window']['size']
	ww, wh = size
	wh = wh - 100
	ww = ww - 150
	size = (ww, wh)
	layout = []
	#settings_menus = ['PTZ Settings', 'Face Detection Settings', 'Object Detection Settings', 'Image\
	#Output Settings', 'Capture Settings', 'Server Settings', 'General Settings']
	#menu_def = [['Settings', [settings_menus]]]
	#menu = sg.MenubarCustom(menu_def, tearoff=True, key='-menubar_key-')

	line1 = [sg.Text('Camera_id:'), sg.Input(default_text=opts['camera_id'], size=(10, 10),\
	enable_events=True, change_submits=True, key='-CAMERA_ID-')]
	cam_src = [sg.Text('Camera Source:'), sg.Input(default_text=src, size=(10, 10), enable_events=True, change_submits=True, key='-CAMERA_SRC-')]
	auth_ckbox = [sg.Checkbox('Requires Authentication', default=False, enable_events=True,\
	key='-HAS_AUTH-')]
	ptz_ckbox = [sg.Checkbox('PTZ Enabled', default=False, enable_events=True, key='-HAS_PTZ-')]
	cam_width = [sg.Text('Camera Width:'), sg.Input(default_text='640', size=(10, 10),\
	enable_events=True, change_submits=True, key='-CAMERA_WIDTH-')]
	cam_height = [sg.Text('Camera Height'), \
		sg.Input(default_text='352', \
		size=(10, 10), \
		enable_events = True, \
		change_submits=True, \
		key='-CAMERA_HEIGHT-')]
	userline = [sg.Text('Username:'), sg.Input(default_text=user, size=(10, 30), enable_events=True, change_submits=True, key='-SET_USER-')] 
	pwline = [sg.Text('Password:'), sg.Input(default_text="", size=(10, 30), password_char = "*", key='-SET_PASS-')]
	line3 = [sg.Button('Add'), sg.Button('Cancel')]
	keyboard_checkbox = [sg.Button('Save Window Location'), sg.Checkbox('Keyboard Control:', default=False, enable_events=True, key='-KEYBOARD_CONTROL-')]
	layout.append(line1)
	layout.append(cam_src)
	layout.append(cam_width)
	layout.append(cam_height)
	layout.append(auth_ckbox)
	layout.append(userline)
	layout.append(pwline)
	layout.append(ptz_ckbox)
	layout.append(line3)
	win = sg.Window('Add Camera', layout, return_keyboard_events=False, location=location, size=size, element_justification='center', finalize=True, resizable=True)
	new_camera_loop(win=win, camera_id=camera_id, opts=opts, src=src)
	return

def new_camera_loop(win=None, camera_id=None, opts=None, src=None):
	global exit_loop
	if camera_id is None:
		camera_id = get_new_id()
	if win is None:
		win = new_camera(camera_id=camera_id, src=src)
	while True:
		if exit_loop == True:
			break
		try:
			window, event, values = sg.read_all_windows(timeout=1)
		except Exception as e:
			log(f"Exit exception:{e}", 'error')
			exit_loop = True
		if event == '__TIMEOUT__':
			pass
		else:
			print(event)
			try:
				print(values[event])
			except:
				pass
			if event == 'Add':
				pw = window['-SET_PASS-'].get()
				auth_key = set_auth(camera_id, pw)
				if src is None:
					src = win['CAMERA_SRC'].get()
					opts['src']['url'] = src
				opts['src']['pw'] = auth_key
				write_opts(opts)
				log(f"Options file written for camera id {camera_id}!", 'info')
				win.close()
				break
			elif event == '-CAMERA_SRC-':
				src = values[event]
				opts['src']['url'] = src
				log(f"Updated camera source! ({src}", 'info')
			elif event == 'Cancel':
				win.close()
				break
			elif event == '-CAMERA_ID-':
				opts['camera_id'] = values[event]
				log(f"Updated camera id! {camera_id}", 'info')
			elif event == '-CAMERA_WIDTH-':
				opts['H'] = values[event]
				log(f"Updated camera height: {values[event]}", 'info')
			elif event == '-CAMERA_HEIGHT-':
				opts['W'] = values[event]
				log(f"Updated camera width: {values[event]}", 'info')
			elif event == '-HAS_AUTH-':
				opts['src']['has_auth'] = values[event]
				log(f"Updated camera authentication flag: {values[event]}", 'info')
			elif event == '-SET_USER-':
				try:
					var = opts['src']
				except:
					opts['src'] = {}
				opts['src']['user'] = values[event]
				log(f"Updated camera height: {values[event]}", 'info')
			elif event == '-HAS_PTZ-':
				opts['has_ptz'] = values[event]
				log(f"Changed ptz enabled value: {values[event]}", 'info')
