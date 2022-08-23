import os
os.add_dll_directory(os.getcwd())
from random import randint
from datetime import timedelta
import datetime as dt
from time import sleep
import vlc
from settingsconfig import*
from threading import Thread
from globals import time_formatting
import globals as g
from .Speak import speak
from .Speak import sapi
from gui.youtube import get_url
from . import subtitle

instance = vlc.Instance()

media_player = instance.media_player_new()

class Player:
	def __init__(self, filename, hwnd):
		self.spoked=""
		self.filename=filename
		self.title=os.path.basename(self.filename)
		self.url=None
		self.repeate_some=False
		self.startpoint=None
		self.endpoint=None
		self.hwnd=hwnd
		self.media=media_player
		self.media.toggle_fullscreen()
		self.sapi=sapi()
		self.set_media(self.filename)
		self.media.set_hwnd(self.hwnd)
		try:
			self.volume=int(get("volume"))
		except:
			self.volume=30
		self.manager = self.media.event_manager()
		self.manager.event_attach(vlc.EventType.MediaPlayerEndReached,self.onEnd)
		self.manager.event_attach(vlc.EventType.MediaPlayerPositionChanged, self.subtitleEvent)
		self.media.play()
		self.media.audio_set_volume(self.volume)

	def onEnd(self,event):
		if event.type == vlc.EventType.MediaPlayerEndReached:
			self.do_reset = True
			Thread(target=self.reset).start()

	def seek(self, seconds):
		length = self.media.get_length()
		if length == -1:
			return 0.03
		try:
			return seconds/(self.media.get_length()/1000)
		except ZeroDivisionError:
			return 0.03

	def get_duration(self):
		duration = self.media.get_length()
		if duration == -1 or not isinstance(duration, int):
			return ""
		return time_formatting(str(timedelta(seconds=duration//1000)))

	def get_elapsed(self):
		elapsed = self.media.get_time()
		if elapsed == -1 or not isinstance(elapsed, int):
			return ""
		return time_formatting(str(timedelta(seconds=elapsed//1000)))

	def reset(self):
		sleep(0.02)
		self.do_reset = False
		if get("repeate"):
			self.media.set_media(self.media.get_media())
			sleep(0.01)
			self.media.play()
		elif get("next_track"):
			if not g.playing_from_youtube:
				if len(g.tracks_list)<1 or g.folder_path=="": return
				if get("random_play"):
					g.index=randint(0, len(g.tracks_list))
				else: g.index+=1
				if g.index>=len(g.tracks_list):
					g.index=0
#					speak(_("تم الإعادة من الملف الأول"))
				p=f"{g.folder_path}/{g.tracks_list[g.index]}"
				self.set_media(p)
				self.media.play()
				g.set_title(self.title)
			else:
				if len(g.tracks_list)<2: return
				if g.random_play:
					g.index=randint(0, len(g.tracks_list))
				else: g.index+=1
				if g.index>=len(g.tracks_list):
					g.index=0
#					speak(_("تم الإعادة من المقطع الأول"))
				data=get_url(g.tracks_list[g.index][1])
				try:
					link=data[0]
				except:
					return
				title=data[2]
				g.set_title(title)
				g.player.filename=title
				g.player.url=g.youtube_url
				self.set_media(link)
				self.media.play()
		else:
			self.media.set_media(self.media.get_media())

	def set_media(self, m):
		sleep(0.01)
		media = instance.media_new(m)
		self.media.set_media(media)
		self.title=os.path.basename(m)
		self.filename=m

	def repeate_some_track(self):
		while self.repeate_some:
			if self.media.get_position()>self.endpoint:
				self.media.set_position(self.startpoint)
			sleep(0.01)

	def subtitleEvent(self,event):
		if not get("read", "subtitles") or g.current_subtitle=={}: return
		if event.type == vlc.EventType.MediaPlayerPositionChanged:
			Thread(target=self.SubtitleCheck).start()

	def SubtitleCheck(self):
		if not get("read", "subtitles") or g.current_subtitle=={}: return
#		if event.type == vlc.EventType.MediaPlayerPositionChanged:
		current=g.time_to_ms(dt.datetime.utcfromtimestamp(self.media.get_time()//1000).strftime("%H:%M:%S"))
		if current in g.current_subtitle and current>=g.time_to_ms(g.current_subtitle[current]["start"]) and current<=g.time_to_ms(g.current_subtitle[current]["end"]):
			text=str(g.current_subtitle[current]["text"]).replace("<i>", "").replace("</i>", "").replace(r"{\i1}", "").replace(r"{\i0}", "")
			sleep(0.5)
			if get("sapi", "subtitles"):
				self.sapi.speak(text) if text!=self.spoked else None
			else:
				speak(text) if text!=self.spoked else None
			self.spoked=text
