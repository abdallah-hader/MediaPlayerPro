from threading import Thread
import os
os.add_dll_directory(os.getcwd())
import ctypes
import platform
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
		from NBSapi import NBSapi
		self.engine=NBSapi()
		voices=self.get_voices()
		voices_list=[i for i in voices]
		try:
			self.set_voice(int(get("voice", "subtitles")))
		except:
			self.set_voice(0)
		self.set_volume(float(get("volume", "subtitles")))
		speed_rate={0:10, 1:70, 2:180, 3:220, 4:300}
		self.set_speed(int(get("speed", "subtitles")))

	def get_voices(self):
		voices_object=self.engine.GetVoices()
		voices={}
		for voice in voices_object:
			voices[voice["Name"]] = [voice["Id"], voice["Language"]]
		return voices

	def set_voice(self, index):
		return self.engine.SetVoice(index)

	def get_speed(self):
		return self.engine.GetRate()

	def set_speed(self, value):
		return self.engine.SetRate(value)

	def get_volume(self):
		return self.engine.GetVolume()

	def set_volume(self, value):
		return self.engine.SetVolume(value)

	def speak(self, text):
#		speak("ok")
		return self.engine.Speak(text)
