def init_keytocode():
	#init key to code dict
	ktc = {}
	ktc['arrow_up'] = 103
	ktc['arrow_down'] = 108
	ktc['arrow_left'] = 105
	ktc['arrow_right'] = 106
	ktc['downleft'] = 79
	ktc['down'] = 80
	ktc['downright'] = 81
	ktc['left'] = 75
	ktc['center'] = 76
	ktc['right'] = 77
	ktc['upleft'] = 71
	ktc['up'] = 72
	ktc['upright'] = 73
	ktc['stop'] = 82
	return ktc

def init_codetokey():
	ctk = {}
	ctk[103] = 'arrow_up'
	ctk[108] = 'arrow_down'
	ctk[105] = 'arrow_left'
	ctk[106] = 'arrow_right'
	ctk[79] = 'downleft'
	ctk[80] = 'down'
	ctk[81] = 'downright'
	ctk[75] = 'left'
	ctk[76] = 'center'
	ctk[77] = 'right'
	ctk[71] = 'upleft'
	ctk[72] = 'up'
	ctk[73] = 'upright'
	ctk[82] = 'stop'
	return ctk
ktc = init_keytocode()
ctk = init_codetokey()
