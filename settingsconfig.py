import configparser
import os

spath=os.path.join(os.getenv("appdata"), "Media Player Pro")
datapath=os.path.join(spath, "data")
playlistspath = os.path.join(spath, "playlists")

defaults={
	"programpath":"C:/Program Files (x86)/MediaPlayerPro",
	"language":"en",
	"volume":50,
	"seek":1,
	"check_for_updates_at_startup":True,
	"languageupdates":True,
	"repeate":True,
	"save_at_exit":False,
	"load_directory_file":False,
	"load_first_file":True,
	"next_track":False,
	"history":True,
	"random_play":False,
	"country":"none",
	"speak_play_pause":True,
	"speakfr":True,
	"speakv":True,
	"speakreplayed":True,
	"speakspeedrate":True
}

shortcuts={
	"hotkeys":"alt+win",
	"replace_pages":False
}

subtitles={
	"read":True,
	"autodetect":False,
	"sapi":False,
	"voice":0,
	"speed":4,
	"volume":40,
}

def s_to_b(what):
	if what=="True":
		return True
	elif what=="False":
		return False
	else:
		return what

def init_config():
	init_sections()
	try:
		os.mkdir(spath)
	except FileExistsError:
		pass
	try:
		os.mkdir(os.path.join(spath, "data"))
	except FileExistsError:
		pass
	try:
		os.mkdir(playlistspath)
	except FileExistsError:
		pass
	if not os.path.exists(os.path.join(spath, "settings.ini")):
		config=configparser.ConfigParser()
		config.add_section("settings")
		config.add_section("keybord")
		config.add_section("subtitles")
		for k,v in defaults.items():
			config["settings"][k]=str(v)
		for k,v in shortcuts.items():
			config["keybord"][k]=str(v)
		for k,v in subtitles.items():
			subtitles[k] = str(v)
		with open(os.path.join(spath, "settings.ini"),"w") as f:
			config.write(f)

def init_sections():
	sections=["settings", "keybord", "subtitles"]
	if not os.path.exists(os.path.join(spath, "settings.ini")): return
	config=configparser.ConfigParser()
	config.read(os.path.join(spath, "settings.ini"))
	for section in sections:
		if config.has_section(section): continue
		config.add_section(section)
	with open(os.path.join(spath, "settings.ini"),"w") as f:
		config.write(f)



def get(string, section="settings"):
	config=configparser.ConfigParser()
	try:
		config.read(os.path.join(spath, "settings.ini"))
		v=config[section][string]
		return s_to_b(v)
	except KeyError:
		if section=="settings":
			new(string, defaults[string])
			return defaults[string]
		elif section=="subtitles":
			new(string, subtitles[string], "subtitles")
			return subtitles[string]
		else:
			new(string, shortcuts[string], "keybord")
			return shortcuts[string]


def new(key, value, section="settings"):
	config = configparser.ConfigParser()
	try:
		config.read(os.path.join(spath, "settings.ini"))
		config[section][key] = str(value)
		with open(os.path.join(spath, "settings.ini"), "w") as f:
			config.write(f)
	except:
		pass