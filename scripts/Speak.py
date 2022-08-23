import os
os.add_dll_directory(os.getcwd())
import ctypes
import platform
import pyttsx3 as ptts
from settingsconfig import get
arch=platform.architecture()[0]
dll = f".\\nvdaControllerClient{'32' if arch == '32bit' else '64'}.dll"
nvda = ctypes.windll.LoadLibrary(dll)

def speak(msg):
	running = nvda.nvdaController_testIfRunning()
	if running != 1:
		nvda.nvdaController_speakText(msg)

class sapi:
	def __init__(self):
		self.engine=ptts.init()
		voices=self.get_voices()
		voices_list=[i for i in voices]
		try:
			self.set_voice(voices[voices_list[int(get("voice", "subtitles"))]][0])
		except:
			self.set_voice(voices[voices_list[int(0)]][0])
		self.set_volume(float(get("volume", "subtitles")))
		speed_rate={0:10, 1:70, 2:180, 3:220, 4:300}
		self.set_speed(speed_rate[int(get("speed", "subtitles"))])



	def get_voices(self):
		voices_object=self.engine.getProperty("voices")
		voices={}
		for voice in voices_object:
			voices[voice.name] = [voice.id, voice.languages]
		return voices

	def get_voice_id(self, name):
		voices=self.get_voices()
		id=None
		for voice in voices:
			if voice==name:
				id=voices[voice][0]
				break
		return id

	def get_voice_name(self, id):
		voices={v:k for k,v[0] in self.get_voices()}
		name=""
		for voice in voices:
			if voice==id:
				name=voices[voice]
				break
		return name

	def set_voice(self, id):
		return self.engine.setProperty("voice", id)

	def get_speed(self):
		return self.engine.getProperty("rate")

	def set_speed(self, value):
		return self.engine.setProperty("rate", value)

	def get_volume(self):
		return self.engine.getProperty("volume")

	def set_volume(self, value):
		return self.engine.setProperty("volume", value)

	def get_voice_language(self, name):
		voices=self.get_voices()
		language=None
		for voice in voices:
			if voice==name:
				language=voices[voice][1]
				break
		return language

	def speak(self, text):
		self.engine.say(text)
		self.engine.runAndWait()
