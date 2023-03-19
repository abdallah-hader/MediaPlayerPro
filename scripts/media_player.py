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
try:
	from .Speak import sapi
except: pass
from gui.youtube import get_url
from . import subtitle

instance = vlc.Instance()

media_player = instance.media_player_new()


class Player:
	def __init__(self, filename="", hwnd=None, mu=False):
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
		try:
			self.sapi=sapi()
		except: self.sapi = None
		if not mu:
			self.set_media(self.filename)
		self.media.set_hwnd(self.hwnd)
		try:
			self.volume=int(get("volume"))
		except:
			self.volume=30
		self.manager = self.media.event_manager()
		self.manager.event_attach(vlc.EventType.MediaPlayerEndReached,self.onEnd)
		self.manager.event_attach(vlc.EventType.MediaPlayerPositionChanged, self.subtitleEvent)
		if not mu:
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

	def get_duration(self, w=0):
		duration = self.media.get_length()
		if duration == -1 or not isinstance(duration, int):
			return ""
		if w==0:
			return time_formatting(str(timedelta(seconds=duration//1000)))
		else:
			return str(timedelta(seconds=duration//1000))

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

	def LoadM3U(self, path):
		mp = instance.media_player_new()
		m = instance.media_list_new([path])
		self.m2 = instance.media_list_player_new()
		self.m2.set_media_list(m)
		self.m2.set_media_player(self.media)
		self.m2.play()
		g.m3u = True
		media_player = self.m2.get_media_player()
		mmedia = media_player.get_media()
		self.title = mmedia.get_meta(vlc.Meta.Title)
		g.set_title(self.title)

	def mnext(self):
		self.m2.next()
		media_player = self.m2.get_media_player()
		mmedia = media_player.get_media()
		self.title = os.path.basename(mmedia.get_meta(vlc.Meta.Title))
		g.set_title(self.title)
		self.filename = mmedia.get_meta(vlc.Meta.Title)

	def mprevious(self):
		self.m2.previous()
		media_player = self.m2.get_media_player()
		mmedia = media_player.get_media()
		self.title = os.path.basename(mmedia.get_meta(vlc.Meta.Title))
		g.set_title(self.title)
		self.filename = mmedia.get_meta(vlc.Meta.Title)

	def set_media(self, m):
		if g.m3u: g.m3u = False
		sleep(0.01)
		media = instance.media_new(m)
		self.media.set_media(media)
		self.title=os.path.basename(m)
		self.filename=m
		g.current_subtitle={}
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
#			if text==self.spoked:
#			speak(str(text==self.spoked))
			sleep(0.5)
			if get("sapi", "subtitles"):
				if not text==self.spoked:
					self.spoked=text
					try:
						g.sapi.speak(text, )
					except: pass
			else:
				speak(text) if text!=self.spoked else None
			self.spoked=text
