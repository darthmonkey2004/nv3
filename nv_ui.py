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
from settings_menu import *
from keymap import ctk
from new_camera import *
from new_object import *

log = nv_logger().log_msg

class nv_ui():
	def __init__(self, camera_id):
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
			self.tour = False
			self.tour = self.opts['ptz']['tour']
			self.tour_started = False
		self.exit = False
		self.win = self.ptz_ui()

	def ptz_ui(self):
		layout = []
		menu_def = [['Settings', [self.settings_menus], 'Oak-D Lite']]
		menu = [sg.MenubarCustom(menu_def, tearoff=True, key='-menubar_key-'), sg.Button('Add Camera')]
		line1 = [sg.Button('Up Left'), sg.Button('Up'), sg.Button('Up Right')]
		line2 = [sg.Button('Left'), sg.Button('Stop'), sg.Button('Right')]
		line3 = [sg.Button('Down Left'), sg.Button('Down'), sg.Button('Down Right')]
		keyboard_checkbox = [sg.Button('Save Window Location'), sg.Checkbox('Keyboard Control:', default=False, enable_events=True, key='-KEYBOARD_CONTROL-'), sg.Checkbox('PTZ Auto Tracking:', default=self.opts['detector']['track_to_center'], enable_events=True, key='-PTZ_TRACKING-')]
		current_memory_box = [sg.Text(psutil.virtual_memory().percent, key='CURRENT_MEMORY')]
		layout.append(menu)
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

	def quit(self):
		log(f"UI: Writing opts file (on exit)...", 'info')
		#send quit command to hub for propagation through the threads.
		write_opts(self.opts)
		kill_nv()
		exit()


	def handle_coms(self):
		self.event, self.vals = None, None
		self.win, self.event, self.vals = sg.read_all_windows(timeout=1)
		if self.event == '__TIMEOUT__':
			return None, None
		if self.event is not None:
			if '=' in self.event:
				self.event, self.vals = self.event.split('=')
			if self.event == 'quit':
				self.exit = True
				log(f"nv_ui:handle_coms():Exit command received! Settings exit=True...", 'info')
			return self.event, self.vals
		else:
			self.com = None
			return None, None

			
		

	def ui_loop(self):
		if self.ptz == None:
			self.ptz = ptz_control()
		if self.win == None:
			self.win = ptz_ui()
		if self.events is True:
			self.ptz.start_loop()
		self.ptz.set_speed(self.ptz_speed)
		preset = None
		tour_dest = 0
		while True:
			event, vals = None, None
			loop_start_ts = round(time.time(), 2)
			if self.tour == True:
				if self.tour_started is None:
					self.tour_started = time.time()
					tour_dest = 0
				else:
					duration = round(time.time() - self.tour_started)
					if duration >= self.tour_wait:
						if tour_dest == 0:
							tour_dest = 1
						elif tour_dest == 1:
							tour_dest = 0
						self.ptz.goto(tour_dest)
						self.tour_started = time.time()
			if self.keyboard_control == True:
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
			
			event, values = self.handle_coms()	
			if event == 'exit' or event == 'quit':
				self.exit = True
				log(f"nv_ui.start():Exit flag set! Quitting...", 'info')
			if self.exit == True:
				self.quit()
				break
			if event is not None:
				if event in self.settings_menus:
					self.win.hide()
					settings(event)
					event_loop()
					self.win.un_hide()
				elif event == 'Add Camera':
					self.win.hide()
					new_camera_loop()
					self.win.un_hide()
				if self.ptz.opts['debug'] == True:
					log(f"EVENT: {event}", 'info')
				if event == 'Quit':
					self.exit = True
					window.close()
				elif event == '-KEYBOARD_CONTROL-':
					self.keyboard_control = values[event]
					log(f"Keyboard events set to {self.keyboard_control}!", 'info')
				elif event == 'Tour Start':
					self.tour = True
					log(f"Tour started!", 'info')
					self.tour_started = None
					tour_dest = 0
				elif event == 'Tour Stop':
					self.tour = False
					self.tour_started = None
					tour_dest = 0
					log(f"Tour stopped!", 'info')
				elif event == '-SELECT_PRESET-':
					preset = values[event]
					print(f"Selected preset: {preset}")
				elif event == 'Goto':
					if preset == None:
						preset = 0
					else:
						self.ptz.goto(preset)
					print(f"Move to preset: {preset}")
				elif event == 'Save Window Location':
					coords = window.CurrentLocation()
					self.opts['ptz']['window']['location'] = coords
					log(f"Current lcoation: {coords}", 'info')
				elif event == sg.WIN_CLOSED:
					try:
						window.close()
						if self.exit == True:
							self.quit()
							break
					except:
						self.exit = True
				elif event == 'Set':
					val = values['-SELECT_PRESET-']
					self.ptz.set_goto(val)
				elif event == '-PTZ_TRACKING-':
					val = values[event]
					self.ptz.set_ptz_track_to_center(val)
					log(f"Toggle PTZ Auto Tracking: {self.ptz.track_to_center}!", 'info')
				else:
					log(f"nv_ui.start():Unhandled event: {event} (vals={vals}", 'warning')
		
			loop_stop_ts = round(time.time(), 2)
			loop_time = loop_stop_ts - loop_start_ts
			log(f"nv_ui:start():Total loop time: {loop_time}", 'info')

	


def run(self):
	win = ptz_ui()
	ui_loop(win)

if __name__ == "__main__":
	start()
	
