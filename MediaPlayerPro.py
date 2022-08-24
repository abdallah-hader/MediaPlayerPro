import threading
import pyperclip
import globals as g
import sys
from time import sleep
from datetime import datetime
import docs_handler
import os
os.chdir	(os.path.abspath(os.path.dirname(__file__)))
os.add_dll_directory(os.getcwd())
import shelve
import wx
from scripts import web_browser as web
from scripts import media_player, instance_running, thread, subtitle
from vlc import State, Media, VLCException
import vlc
from scripts.Speak import speak
from scripts.Speak import sapi
from settingsconfig import*
from language import init_translation
from gui import youtube, search, input_box, history, comments, favorite, help_dialog, updater, settings_dialog
import application

init_translation("MediaPlayerPro") #init the translation for the program
init_config() #initialize the program settings file

def has_player(method):
	"""
a decorater to check if there is a player or not, to stop executeing some functions when call its
	"""
	def rapper(self, *args):
		if g.player is not None:
			method(self, *args)
		else: return speak(_("لم يتم تشغيل ملف بعد..."))
	return rapper

class main(wx.Frame):
#the main window class
	def __init__(self, path):
		self.temp=os.path.join(os.getenv("temp"), "mpp.txt")
		t=open(self.temp, "w")
		t.write(":::=false")
		t.close()
		running = instance_running.check("mediaplayerpro", os.getpid())
		if running:
			if not path:
				wx.MessageBox(_("هناك نسخة مِن البرنامج تعمل بالفعل"), _("خطأ"), style=wx.ICON_ERROR)
				return
			with open(self.temp, "w", encoding="utf-8") as temp:
				temp.write(str(path)+":::=true")
				return sys.exit()
		wx.Frame.__init__(self, parent=None, title=application.name)
		self.SetupHotKeys()
		self.Center()
		self.SetSize(wx.DisplaySize())
		self.Maximize(True)
		g.parent=self
		g.sapi = sapi()
		threading.Thread(target=updater.cfu, args=[True]).start() if get("check_for_updates_at_startup") else None
		self.types=['mp3','mp4','ogg','m4a','wav','occ'] #files typs to select them when open a folder
		self.loading=False
		g.handle=self.GetHandle()
		self.length=0
		self.opened=0
		self.Bind(wx.EVT_KEY_DOWN, self.shortcuts)
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.oloop=True
		self.threadloop=thread.Thread(self.openloop)
		self.threadloop.start()
		if get("save_at_exit") and not path:
			self.load_last()
		if path:
			self.play_from_path(path)
		self.MenuBarSetup()
		self.Show()

	def MenuBarSetup(self):
		menubar=wx.MenuBar()
		MainMenu=wx.Menu()
		OptionsMenu=wx.Menu()
		YoutubeMenu=wx.Menu()
		about=wx.Menu()
		contact=wx.Menu()
		menubar.Append(MainMenu, _("القائمة الرئيسية"))
		menubar.Append(OptionsMenu, _("الخيارات"))
		menubar.Append(YoutubeMenu, _("يوتيوب"))
		menubar.Append(about, _("حول"))
		user_guide=about.Append(-1, _("دليل المستخدم: f1"))
		TelegramChannel=about.Append(-1, _("قناة البرنامج على تليجرام"))
		about_the_program=about.Append(-1, _("حول البرنامج"))
		about.AppendSubMenu(contact, _("التواصل معنا"))
		openfile=MainMenu.Append(-1, _("فتح ملف: ctrl+o"))
		open_folder = MainMenu.Append(-1, _("فتح مجلد: ctrl+f"))
		open_subtitle = MainMenu.Append(-1, _("فتح ملف ترجمة (srt): ctrl+shift+s"))
		youtube_search=YoutubeMenu.Append(-1, _("البحث في يوتيوب: a"))
		from_url = YoutubeMenu.Append(-1, _("تشغيل مِن رابط: y"))
		history = YoutubeMenu.Append(-1, _("سجل البحث: ctrl+h"))
		GetComments = YoutubeMenu.Append(-1, _("عرض تعليقات المقطع الحالي: c"))
		CopyDescription = YoutubeMenu.Append(-1, _("نسخ الوصف: ctrl+i"))
		ShowFavorite = OptionsMenu.Append(-1, _("المفضلة: f"))
		addfavorite =OptionsMenu.Append(-1, _("إضافة للمفضلة: ctrl+p"))
		folder_search = OptionsMenu.Append(-1, _("البحث في المجلد: s"))
		go_to = OptionsMenu.Append(-1, _("الذهاب إلى: g"))
		random_choos = OptionsMenu.Append(-1, _("الإختيار العشوائي: ctrl+r"))
		settings = MainMenu.Append(-1, _("الإعدادات: ctrl+s"))
		update=MainMenu.Append(-1, _("البحث عن تحديثات"))
		close=MainMenu.Append(-1, _("خروج"))
		telegram=contact.Append(-1, _("تليجرام"))
		facebook=contact.Append(-1, _("فيسبوك"))
		twitter=contact.Append(-1, _("تويتر"))
		self.Bind(wx.EVT_MENU, self.OnCopyDescription, CopyDescription)
		self.Bind(wx.EVT_MENU, lambda e:favorite.favoritegui(self), ShowFavorite)
		self.Bind(wx.EVT_MENU, lambda e:subtitle.Select(), open_subtitle)
		self.Bind(wx.EVT_MENU, self.set_random, random_choos)
		self.Bind(wx.EVT_MENU, self.GetComments, GetComments)
		self.Bind(wx.EVT_MENU, self.ShowHistory, history)
		self.Bind(wx.EVT_MENU, self.add_to_favorite, addfavorite)
		self.Bind(wx.EVT_MENU, self.search, folder_search)
		self.Bind(wx.EVT_MENU, self.goto, go_to)
		self.Bind(wx.EVT_MENU, self.ytsearch, youtube_search)
		self.Bind(wx.EVT_MENU, lambda e:web.Open("https://t.me/mediaplayerpro"), TelegramChannel)
		self.Bind(wx.EVT_MENU, lambda e:web.Open("https://t.me/abdallah_alanbry"), telegram)
		self.Bind(wx.EVT_MENU, lambda e: web.Open("https://twitter.com/abdallahhayder5"), twitter)
		self.Bind(wx.EVT_MENU, lambda e: web.Open("https://m.facebook.com/profile.php?id=100009657259379"), facebook)
		self.Bind(wx.EVT_MENU, self.OnOpen, openfile)
		self.Bind(wx.EVT_MENU, self.CheckForUpdates, update)
		self.Bind(wx.EVT_MENU, self.OnClose, close)
		self.Bind(wx.EVT_MENU, self.OnFolder, open_folder)
		self.Bind(wx.EVT_MENU, self.play_from_youtube, from_url)
		self.Bind(wx.EVT_MENU, lambda e: settings_dialog.settingsgui(self), settings)
		self.Bind(wx.EVT_MENU, self.AboutMessage, about_the_program)
		self.Bind(wx.EVT_MENU, self.ShowUserGuide, user_guide)
		self.SetMenuBar(menubar)
		shortcuts = wx.AcceleratorTable((
			(wx.ACCEL_CTRL, ord("O"), openfile.GetId()),
			(0, wx.WXK_F1, user_guide.GetId()),
			(wx.ACCEL_CTRL, ord("F"), open_folder.GetId()),
			(wx.ACCEL_CTRL+wx.ACCEL_SHIFT, ord("S"), open_subtitle.GetId()),
			(0, ord("A"), youtube_search.GetId()),
			(0, ord("Y"), from_url.GetId()),
			(wx.ACCEL_CTRL, ord("h"), history.GetId()),
			(0, ord("C"), GetComments.GetId()),
			(wx.ACCEL_CTRL, ord("I"), CopyDescription.GetId()),
			(0, ord("F"), ShowFavorite.GetId()),
			(wx.ACCEL_CTRL, ord("P"), addfavorite.GetId()),
			(0, ord("S"), folder_search.GetId()),
			(0, ord("G"), go_to.GetId()),
			(wx.ACCEL_CTRL, ord("R"), random_choos.GetId()),
			(wx.ACCEL_CTRL, ord("S"), settings.GetId()),
		))
		self.SetAcceleratorTable(shortcuts)

	def ShowUserGuide(self, event):
		value=docs_handler.get_doc()
		if value is False: return
		help_dialog.help(self, value)

	def AboutMessage(self, event):
		about=_("""
{name}:
الإصدار: {version}.
المُطوِر: {author}.
الوصف: برنامج يُسَهِل على مستخدمي قارئات الشاشة تشغيل مختلف الوسائط والتحكم بها بشكل سهل ومِن أي مكان من داخل البرنامج أو مِن خارجه مع إتاحة تحكمات النطق للمستخدم في حال أراد تفعيلها أو تعطيلها...""").format(name=application.name, version=application.version, author=application.author)
		wx.MessageBox(about, _("حول البرنامج"), parent=self)

	def CheckForUpdates(self, event):
		speak(_("يتم التحقق من وجود تحديث جديد ، يرجى الانتظار"))
		updater.cfu()

	def OnOpen(self, event):
		path=wx.FileSelector(_("فتح ملف"),parent=self)
		if not path: return
		self.new_track(path)
		g.tracks_list=[]
		self.load_dir(path) if get("load_directory_file") else None

	def load_dir(self, path):
		g.tracks_list=[]
		g.folder_path=os.path.dirname(path)
		threading.Thread(target=self.open_folder, args=[os.path.dirname(path), path]).start()

	def OnFolder(self, event):
		dlg = wx.DirDialog(self, _("قم بإختيار المجلد الذي تريد فتحه في البرنامج..."))
		if dlg.ShowModal() == wx.ID_OK:
			g.folder_path=dlg.GetPath().replace("\\", "/").replace("%20", " ")
			self.open_folder(g.folder_path, from_option=True)

	def play(self, event=None):
		if g.player is None: return speak(_("لم يتم تشغيل ملف بعد..."))
		state = g.player.media.get_state()
		if state in (State.NothingSpecial, State.Stopped):
			g.player.media.play()
			speak(_("تم إعادة تشغيل المقطع")) if get("speak_play_pause") else None
		elif state in (State.Playing, State.Paused):
			g.player.media.pause()
			if state==State.Playing:
				speak(_("تم الإيقاف المؤقت")) if get("speak_play_pause") else None
			else:
				speak(_("تم الإستئناف")) if get("speak_play_pause") else None
		else: 
			g.player.media.stop()
			speak(_("تم إيقاف الملف")) if get("speak_play_pause") else None

	def new_track(self, fn):
		self.Title=f"{os.path.basename(fn)} {application.name}"
		if g.playing_from_youtube: g.playing_from_youtube=not g.playing_from_youtube
		g.current_subtitle = {}
		subtitle.auto_detect(fn) if get("autodetect", "subtitles") else None
		if g.player is None:
			g.player=media_player.Player(fn, self.GetHandle())
			return
		try:
			g.player.media.stop()
		except: pass
		try:
			g.player.set_media(fn)
			g.player.media.play()
			if not g.player.media.will_play():
				g.player.stop()
				g.player=None
		except VLCException():
			speak(_("لا يمكن تشغيل هذا المقطع"))

	def play_from_path(self, path):
		g.tracks_list=[]
		g.folder_path=""
		if os.path.isfile(path):
			self.new_track(path)
			self.load_dir(path) if get("load_directory_file") else None
		elif os.path.isdir(path):
			self.load_dir(path)

	def search(self, event=None):
		r=search.FolderSearch(self)
		if r.Done:
			self.new_track(f"{g.folder_path}/{g.tracks_list[g.index]}")

	@has_player
	def delete(self, event=None):
		if g.playing_from_youtube: return
		file=g.tracks_list[g.index]
		msg=wx.MessageBox(_("هل أنت متأكد بأنك تريد حذف الملف {f}. في حال تم الحذف لا يمكنك إسترجاعه مرةً أُخرى").format(f=file), _("تنبيه"), style=wx.YES_NO, parent=self)
		if msg==wx.YES:
			self.new_track(f"{g.folder_path}/{g.tracks_list[g.index-1]}")
			g.index-=1
			g.tracks_list.remove(file)
			os.remove(f"{g.folder_path}/{file}")
			speak(_("تم حذف {f}").format(f=file))

	def ShowHistory(self, event=None):
		h=history.historygui(self)
		h.ShowModal()

	def ytsearch(self, event=None):
		if not hasattr(g, "search_window"):
			g.search_window=youtube.SearchDialog(self)
			for i in g.search_window.p.GetChildren():
				i.Hide() if i.Name=="result" else None
			g.search_window.Show()
			g.search_window.query.SetFocus()
		else:
#			if not g.search_window.Parent==self:
#				g.search_window.Parent=self
			g.search_window.Show()
			g.search_window.Results.SetFocus()

	def GetComments(self, event=None):
		if not g.playing_from_youtube:
			return speak(_("لم يتم التشغيل من يوتيوب"))
		comments.comments(self, g.youtube_url)

	@has_player
	def OnCopyDescription(self, event):
		if not g.playing_from_youtube: return speak(_("لم يتم التشغيل من يوتيوب"))
		if g.youtube_description !="":
			pyperclip.copy(str(g.youtube_description))
			return speak(_("تم نسخ الوصف إلى الحافظة"))
		speak(_("لا يوجد وصف لنسخه"))

	@has_player
	def forward(self,event=None):
		position = g.player.media.get_position()
		if g.player.repeate_some:
			g.player.media.set_position(position+g.player.seek(int(get("seek"))))
			if g.player.media.get_position()>g.player.endpoint:
				g.player.media.set_position(g.player.endpoint)
		else:
			g.player.media.set_position(position+g.player.seek(int(get("seek"))))
		speak(f"{g.player.get_elapsed()}") if get("speakfr") else None

	@has_player
	def rewind(self, event=None):
		position = g.player.media.get_position()
		if g.player.repeate_some:
			g.player.media.set_position(position-g.player.seek(int(get("seek"))))
			if g.player.media.get_position()<g.player.startpoint:
				g.player.media.set_position(g.player.startpoint)
		else:
			g.player.media.set_position(position-g.player.seek(int(get("seek"))))
		speak(f"{g.player.get_elapsed()}") if get("speakfr") else None

	@has_player
	def set_position_by_numbers(self, num):
		position=int(chr(num))/10
		g.player.media.set_position(position)
		speak(f"{g.player.get_elapsed()}") if get("speakfr") else None

	@has_player
	def set_random(self, event):
		if get("random_play"):
			new("random_play", False)
			speak(_("تم تعطيل التشغيل العشوائي"))
		else:
			new("random_play", True)
			speak(_("تم تفعيل التشغيل العشوائي"))

	@has_player
	def replay(self, event=None):
		if g.player.repeate_some:
			g.player.media.set_position(g.player.startpoint)
		else:
			g.player.media.set_position(0.0)
		if g.player.media.get_state() in (State.NothingSpecial, State.Stopped):
			g.player.media.play()
		speak(_("تم إعادة تشغيل المقطع")) if get("speakreplayed") else None

	@has_player
	def IncreaceSpeedRate(self):
		current=g.player.media.get_rate()
		if round(current, 2)>=2.0:
			return speak(_("تم تعيين أقصى قيمة للسرعة")) if get("speakspeedrate") else None
		g.player.media.set_rate(current+0.1)
		speak(_("تم تعيين السرعة على {rate}").format(rate=round(g.player.media.get_rate(), 2))) if get("speakspeedrate") else None

	@has_player
	def DecreaceSpeedRate(self):
		current=g.player.media.get_rate()
		if round(current, 2)<=0.5:
			return speak(_("تم تعيين أدنى قيمة للسرعة")) if get("speakspeedrate") else None
		g.player.media.set_rate(current-0.1)
		speak(_("تم تعيين السرعة على {rate}").format(rate=round(g.player.media.get_rate(), 2))) if get("speakspeedrate") else None

	@has_player
	def IncreaceVolume(self, event=None):
		if g.player.volume>=200:
			g.player.volume=200
			return
		g.player.volume+=5
		g.player.media.audio_set_volume(g.player.volume)
		new("volume", g.player.volume)
		speak(f"{g.player.volume} %") if get("speakv") else None

	@has_player
	def DecreaceVolume(self, event=None):
		if g.player.volume<=0:
			g.player.volume=0
			return
		g.player.volume-=5
		g.player.media.audio_set_volume(g.player.volume)
		new("volume", g.player.volume)
		speak(f"{g.player.volume} %") if get("speakv") else None

	@has_player
	def set_mute(self, event=None):
		try:
			if g.player.media.audio_get_mute():
				g.player.media.audio_set_mute(False)
				speak(_("تم إلغاء كتم الصوت"))
			else:
				g.player.media.audio_set_mute(True)
				speak(_("تم كتم الصوت"))
		except:
			return speak(_("لا يمكن كتم الصوت"))

	@has_player
	def info(self, event=None):
		if g.player.media.get_state()==State.NothingSpecial:
			return speak(_("تم إنتهاء تشغيل المقطع"))
		if g.playing_from_youtube:
			return speak(g.youtube_file_info)
		return speak(_("{title}, المدة: {duration}, الوقت المُنقَضي: {elapsed}, مستوى الصوت الحالي: {volume}").format(duration=g.player.get_duration(), title=g.player.title, elapsed=g.player.get_elapsed(), volume=g.player.volume))

	def OnClose(self, event):
		self.threadloop.stop()
		if not g.player==None and g.player.repeate_some: g.player.repeate_some=False
		try:
			os.remove(self.temp)
		except:
			pass
		if g.player==None or g.FavoriteLoaded: return wx.Exit()
		if not get("save_at_exit"): return wx.Exit()
		position = g.player.media.get_position()
		if g.playing_from_youtube:
			data=[g.player.title, g.player.url, position, g.tracks_list, True,]
		else: data=[g.player.filename, position, False]
		with shelve.open(os.path.join(datapath, "data")) as f:
			f["data"]=data
		sleep(0.05)
		wx.Exit()

	def load_last(self):
		try:
			with shelve.open(os.path.join(datapath, "data")) as f:
				if f["data"]==[]: return
				if not f["data"][-1]:
					self.load_dir(f["data"][0]) if get("load_directory_file") else None
					self.new_track(f["data"][0])
					g.player.media.set_position(float(f['data'][1]))
				else:
					self.play_from_youtube(f["data"][1], True)
					g.youtube_url=f["data"][1]
					g.player.media.set_position(float(f['data'][2]))
					g.tracks_list=f["data"][3]
		except Exception as e:
			speak("error"+str(e))

	def open_folder(self, path, title="", from_option=False):
		if g.playing_from_youtube: g.playing_from_youtube=False
		g.tracks_list=[]
		self.loading=True
		for name in os.listdir(path):
			if not name.split(".")[-1] in self.types: continue
			if not "." in name: continue
			self.length+=1
		for name in os.listdir(path):
			if not name.split(".")[-1] in self.types: continue
			if not "." in name: continue
			g.tracks_list.append(name)
			self.opened+=1
		try:
			if from_option==True:
				if get("load_first_file"):
					self.new_track(f"{g.folder_path}/{g.tracks_list[0]}")
					g.index=0
				else: pass
		except Exception as e: pass
		if not from_option: g.index=0
		self.loading=False

	def play_from_youtube(self, url="", HasUrl=False):
		if HasUrl:
			data=youtube.get_url(url)
		else:
			link = input_box.Input(self, _("الرابط"), _("قم بإدخال رابط اليوتيوب المُراد تشغيله"))
			if link.canceled: return
			url=link.text()
			g.youtube_url=url
			data=youtube.get_url(link.text())
		try:
			link=data[0]
		except:
			return
		title=data[2]
		g.youtube_file_info=data[1]
		if g.player is None:
				g.player=media_player.Player(link, self.GetHandle())
				g.playing_from_youtube=True
				self.Title=f"{title} {application.name}"
				g.player.title=title
				g.player.url=url
				return
		try:
			g.player.media.stop()
		except: pass
		g.player.set_media(link)
		g.playing_from_youtube=True
		self.Title=f"{title} {application.name}"
		g.player.title=title
		g.player.url=url
		g.folder_path=""
		g.player.media.play()
		g.youtube_url=url
		with open(self.temp, "w") as t:
			t.write("youtube:::=false")

	def next(self, event=None):
		if self.loading: return speak(_("يتمفتح المجلد {} / {}").format(self.opened, self.length))
		if len(g.tracks_list)<2: return speak(_("لا يوجد هناك مجلد"))
		g.index+=1
		if g.index>=len(g.tracks_list):
			g.index=0
			speak(_("تم الإعادة من المقطع الأول"))
		self.new_track(f"{g.folder_path}/{g.tracks_list[g.index]}") if not g.FavoriteLoaded else 		self.new_track(f"{g.tracks_list[g.index]}")

	def previous(self, event=None):
		if self.loading: return speak(_("يتمفتح المجلد {} / {}").format(self.opened, self.length))
		if len(g.tracks_list)<2: return speak(_("لا يوجد هناك مجلد"))
		if g.index<=0:
			g.index=len(g.tracks_list)
			speak(_("تم الإنتقال إلى آخِر ملف"))
		g.index-=1
		self.new_track(f"{g.folder_path}/{g.tracks_list[g.index]}") if not g.FavoriteLoaded else 		self.new_track(f"{g.tracks_list[g.index]}")

	def go_to_previous(self, event=None):
		if not g.playing_from_youtube:
			self.previous()
		else:
			self.previous_youtube_video()

	def go_to_next(self, event=None):
		if not g.playing_from_youtube:
			self.next()
		else:
			self.next_youtube_video()

	def next_youtube_video(self, event=None):
		if len(g.tracks_list)<2: return speak(_("لا توجد هناك قائمة"))
		g.index+=1
		if g.index>=len(g.tracks_list):
			g.index=0
			speak(_("تم الإعادة من المقطع الأول"))
		threading.Thread(target=self.play_from_youtube, args=[g.tracks_list[g.index][1], True]).start()

	def previous_youtube_video(self, event=None):
		if len(g.tracks_list)<2: return speak(_("لا توجد هناك قائمة"))
		if g.index<=0:
			g.index=len(g.tracks_list)
			speak(_("تم الإنتقال إلى آخِر مقطع"))
		g.index-=1
		threading.Thread(target=self.play_from_youtube, args=[g.tracks_list[g.index][1], True]).start()


	def goto(self, event=None):
		if self.loading: return speak(_("يتمفتح المجلد {} / {}").format(self.opened, self.length))
		if len(g.tracks_list)<2 or g.folder_path=="": return speak(_("لا يوجد هناك مجلد"))
		number=InputBox.Input(self, _("الذهاب إلى"), _("اكتب رقم الملف لتشغيله, 0/{l}").format(l=len(g.tracks_list)), Max=len(g.tracks_list), num=True, position=g.index)
		if number.canceled: return
		g.index=number.text()
		if g.index>=len(g.tracks_list):
			g.index=0
			speak(_("تم الإعادة من الملف الأول"))
		self.new_track(f"{g.folder_path}/{g.tracks_list[g.index]}")

	def set_repeate(self,event=None):
		if get("repeate"):
			speak(_("تم تعطيل التكرار"))
			new("repeate", False)
		else:
			speak(_("تم تفعيل التكرار"))
			new("repeate", True)

	def set_next_track(self, event=None):
		if get("next_track"):
			new("next_track", False)
			speak(_("تم تعطيل تشغيل الملف التالي"))
		else:
			new("next_track", True)
			speak(_("تم تمكين تشغيل الملف التالي"))

	def ShowHide(self, event=None):
		self.Show(not self.Shown)
		if self.Shown:
			speak(_("تم إظهار البرنامج"))
		else:
			speak(_("تم إخفاء البرنامج, اضغط على الإختصار العام لديك + h لإظهاره"))



	def shortcuts(self, event):
		if get("replace_pages", "keybord") and event.shiftDown and event.GetKeyCode()==wx.WXK_TAB:
			self.go_to_previous()
		elif get("replace_pages", "keybord") and event.GetKeyCode()==wx.WXK_TAB:
			self.go_to_next()
		elif event.GetKeyCode() == wx.WXK_F5:
			current = int(get("speed", "subtitles"))
			if current>0:
				g.sapi.set_speed(current-1)
				new("speed", g.sapi.get_speed(), "subtitles")
				speak(_("تم تعيين السرعة على {s}").format(s=int(get("speed", "subtitles"))))
		elif event.GetKeyCode() == wx.WXK_F6:
			current = int(get("speed", "subtitles"))
			if current<10:
				g.sapi.set_speed(current+1)
				new("speed", g.sapi.get_speed(), "subtitles")
				speak(_("تم تعيين السرعة على {s}").format(s=int(get("speed", "subtitles"))))
		elif event.GetKeyCode() == wx.WXK_F7:
			current = int(get("volume", "subtitles"))
			if current>5:
				g.sapi.set_volume(current-5)
				new("volume", g.sapi.get_volume(), "subtitles")
				speak(_("تم تعيين مستوى الصوت على {v}%").format(v=int(get("volume", "subtitles"))))
		elif event.GetKeyCode() == wx.WXK_F8:
			current = int(get("volume", "subtitles"))
			if current<100:
				g.sapi.set_volume(current+5)
				new("volume", g.sapi.get_volume(), "subtitles")
				speak(_("تم تعيين مستوى الصوت على {v}%").format(v=int(get("volume", "subtitles"))))

		if event.controlDown and event.GetKeyCode()==ord("W"):
			with shelve.open(os.path.join(datapath, "data")) as f:
				f["data"]=[]
			try:
				g.player.media.stop()
				g.player.filename=""
				g.player.url=""
				g.player.startpoint=None
				g.player.endpoint=None
				g.player.repeate_some=False
				g.player=None
				g.folder_path=""
				g.tracks_list=[]
				g.playing_from_youtube=False
				g.set_title("")
			except: pass
		key=event.GetKeyCode()
		if key==wx.WXK_SPACE:
			self.play()
		elif key==ord("Q"):
			if g.player is None or g.player.repeate_some: return
			g.player.startpoint=g.player.media.get_position()
			speak(_("تم تعيين نقطة البداية"))
		elif key==ord("W"):
			if g.player is None or g.player.repeate_some: return
			g.player.endpoint=g.player.media.get_position()
			speak(_("تم تعيين نقطة النهاية"))
		elif key==ord("-"):
			self.DecreaceSpeedRate()
		elif key==ord("="):
			self.IncreaceSpeedRate()
		elif key==wx.WXK_F2 and not g.player is None:
			if g.player.endpoint is None or g.player.startpoint is None or g.player.startpoint>g.player.endpoint: return speak(_("لا يتناسَق وقت نقطة البداية مع وقت نقطة النهاية"))
			if g.player.repeate_some==True:
				g.player.repeate_some=False
				speak(_("تم إيقاف تكرار المقطع المحدد"))
			else:
				speak(_("تم تمكين تكرار المقطع المحدد"))
				g.player.repeate_some=True
				threading.Thread(target=g.player.repeate_some_track).start()
		elif key==ord("0"):
			e=vlc.AudioEqualizer()
			g.player.media.set_equalizer(e)
			e.set_preamp(3)
			e.release()
		elif key==wx.WXK_RIGHT:
			self.forward()
		elif not get("replace_pages", "keybord") and key==wx.WXK_PAGEDOWN:
			self.go_to_next()
		elif not get("replace_pages", "keybord") and key==wx.WXK_PAGEUP:
			self.go_to_previous()
		elif key==wx.WXK_LEFT:
			self.rewind()
		elif key==wx.WXK_UP:
			self.IncreaceVolume()
		elif key==wx.WXK_DOWN:
			self.DecreaceVolume()
		elif key==wx.WXK_DELETE or key==wx.WXK_NUMPAD_DELETE:
			self.delete()
		elif key==wx.WXK_HOME:
			self.replay()
		elif key==ord("I"):
			self.info()
		elif key==ord("N"):
			self.set_next_track()
		elif key==ord("R"):
			self.set_repeate()
		elif key == ord("M"):
			self.set_mute()
		elif key==ord("G"):
			self.goto()
		elif event.KeyCode in range(49, 58):
			if g.player is not None and g.player.repeate_some: return
			self.set_position_by_numbers(event.KeyCode)
		event.Skip()

	def SetupHotKeys(self,):
		h=get("hotkeys", section="keybord")
		k=wx.MOD_NONE
		if "win" in h:
			k=k+wx.MOD_WIN
		if "alt" in h:
			k=k+wx.MOD_ALT
		if "control" in h:
			k=k+wx.MOD_CONTROL
		if "shift" in h:
			k=k+wx.MOD_SHIFT
		self.ShowHideId=wx.NewIdRef()
		self.ForwardId=wx.NewIdRef()
		self.RewindId=wx.NewIdRef()
		self.ReplayId=wx.NewIdRef()
		self.MuteId=wx.NewIdRef()
		self.PauseId=wx.NewIdRef()
		self.VolumeUpId=wx.NewIdRef()
		self.VolumeDownId=wx.NewIdRef()
		self.InfoId=wx.NewIdRef()
		self.NextId=wx.NewIdRef()
		self.PreviousId=wx.NewIdRef()
		self.RepeateId=wx.NewIdRef()
		self.YoutubeId=wx.NewIdRef()
		self.GotoId=wx.NewIdRef()
		self.OpenFileId=wx.NewIdRef()
		self.OpenFolderId=wx.NewIdRef()
		self.DelId=wx.NewIdRef()
		self.YTID=wx.NewIdRef()
		self.Bind(wx.EVT_HOTKEY, self.ytsearch, self.YTID)
		self.Bind(wx.EVT_HOTKEY, self.delete, self.DelId)
		self.Bind(wx.EVT_HOTKEY, self.OnOpen, self.OpenFileId)
		self.Bind(wx.EVT_HOTKEY, self.OnFolder, self.OpenFolderId)
		self.Bind(wx.EVT_HOTKEY, self.goto, self.GotoId)
		self.Bind(wx.EVT_HOTKEY, self.ShowHide, id=self.ShowHideId)
		self.Bind(wx.EVT_HOTKEY, self.play_from_youtube, id=self.YoutubeId)
		self.Bind(wx.EVT_HOTKEY, self.go_to_next, id=self.NextId)
		self.Bind(wx.EVT_HOTKEY, self.go_to_previous, id=self.PreviousId)
		self.Bind(wx.EVT_HOTKEY, self.set_repeate, id=self.RepeateId)
		self.Bind(wx.EVT_HOTKEY, self.info, id=self.InfoId)
		self.Bind(wx.EVT_HOTKEY, self.IncreaceVolume, id=self.VolumeUpId)
		self.Bind(wx.EVT_HOTKEY, self.DecreaceVolume, id=self.VolumeDownId)
		self.Bind(wx.EVT_HOTKEY, self.play, id=self.PauseId)
		self.Bind(wx.EVT_HOTKEY, self.set_mute, id=self.MuteId)
		self.Bind(wx.EVT_HOTKEY, self.replay, id=self.ReplayId)
		self.Bind(wx.EVT_HOTKEY, self.forward, id=self.ForwardId)
		self.Bind(wx.EVT_HOTKEY, self.rewind, id=self.RewindId)
		self.RegisterHotKey(self.YTID, k, ord("A"))
		self.RegisterHotKey(self.DelId, k, wx.WXK_DELETE or wx.WXK_NUMPAD_DELETE)
		self.RegisterHotKey(self.OpenFileId, k, ord("O"))
		self.RegisterHotKey(self.OpenFolderId, k, ord("S"))
		self.RegisterHotKey(self.GotoId, k, ord("J"))
		self.RegisterHotKey(self.ShowHideId, k, ord("H"))
		self.RegisterHotKey(self.YoutubeId, k, ord("L"))
		self.RegisterHotKey(self.NextId, k, wx.WXK_PAGEDOWN if not get("replace_pages", "keybord") else ord("X"))
		self.RegisterHotKey(self.PreviousId, k, wx.WXK_PAGEUP if not get("replace_pages", "keybord") else ord("Z"))
		self.RegisterHotKey(self.RepeateId, k, ord("E"))
		self.RegisterHotKey(self.InfoId, k, ord("I"))
		self.RegisterHotKey(self.VolumeUpId, k, wx.WXK_UP)
		self.RegisterHotKey(self.VolumeDownId, k, wx.WXK_DOWN)
		self.RegisterHotKey(self.PauseId, k, wx.WXK_SPACE)
		self.RegisterHotKey(self.MuteId, k, ord("V"))
		self.RegisterHotKey(self.ReplayId, k, wx.WXK_HOME)
		self.RegisterHotKey(self.RewindId, k, wx.WXK_LEFT)
		self.RegisterHotKey(self.ForwardId, k, wx.WXK_RIGHT)

	def openloop(self):
		while g.pathloop:
			self.tempcheck()
			sleep(0.01)

	def tempcheck(self):
		try:
			with open(self.temp, "r", encoding="utf-8") as f:
				t=f.read()
				temp=t.split(":::=")
				if temp[1]=="true":
					self.new_track(str(temp[0])) if temp[0]!=g.player.filename else None
			with open(self.temp, "w", encoding="utf-8") as temp2:
				temp2.write(t.replace(":::=true", ":::=false"))
		except Exception as e:
			pass

	@has_player
	def add_to_favorite(self, event):
		dt=datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
		info={
			"title":g.player.title,
			"position":g.player.media.get_position(),
			"elapsed":g.player.get_elapsed(),
			"is_url":False if not g.playing_from_youtube else True,
			"path":g.player.filename if not g.playing_from_youtube else None,
			"url":g.youtube_url if g.playing_from_youtube else None,
					"added_time":dt
		}
		favorite.AddFavorite(self, g.player.title, info)

app=wx.App()
FromPath=None
if len(sys.argv)>1:
	FromPath=" ".join(sys.argv[1::]).replace("\\", "/")
if __name__=="__main__":
	main(FromPath)
	app.MainLoop()