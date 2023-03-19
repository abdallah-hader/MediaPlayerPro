import wx
import os
import globals as g
from settingsconfig import playlistspath as ppath
from scripts import media_player
from scripts.Speak import speak
from . import input_box

class PlaylistsDialog(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, -1, title=_("قوائم التشغيل"))
		self.CenterOnParent()
		p = wx.Panel(self)
		self.m = PlaylistsManager() # an instance of the manager class to manage playlists
		wx.StaticText(p, -1, _("قوائم التشغيل"))
		self.playlistsList = wx.ListBox(p, -1)
		self.newList = wx.Button(p, -1, _("إنشاء قائمة تشغيل جديدة"))
		self.newList.Bind(wx.EVT_BUTTON, self.OnNewList)
		self.close = wx.Button(p, wx.ID_CANCEL, _("إغلاق"))
		self.close.Bind(wx.EVT_BUTTON, self.OnClose)
		self.Bind(wx.EVT_CHAR_HOOK, self.OnList)
		self.ListInit()
		self.ContextSetup()
		self.Show()

	def OnClose(self, evt):
		if not self.FindFocus() == self.close: return
		self.Destroy()

	def ListInit(self):
		self.playlistsList.Clear()
		self.m.initialize()
		if not self.m.lists: return
		for i in self.m.lists:
			self.playlistsList.Append(self.m.lists[i]["name"])
		self.playlistsList.Selection = 0

	def OnList(self, event):
		key = event.GetKeyCode()
		if key == wx.WXK_ESCAPE:
			self.Destroy()
		elif key == wx.WXK_RETURN and self.FindFocus()==self.playlistsList:
			playlist(self, self.playlistsList.StringSelection)
		elif key == wx.WXK_DELETE and self.FindFocus()==self.playlistsList:
			self.OnDelete(None)
		event.Skip()

	def OnNewList(self, event):
		if not self.FindFocus() == self.newList: return
		pl = input_box.Input(self, _("إنشاء قائمة تشغيل جديدة"), _("قم بإدخال اسم قائمة التشغيل الجديدة"))
		if pl.canceled or not pl.text(): return
		if self.m.new(f"{pl.text()}.m3u"):
			speak(_("تم إنشاء قائمة التشغيل {P} بنجاح").format(P=pl.text()))
			self.ListInit()
			self.playlistsList.Selection = self.playlistsList.FindString(pl.text())
		else:
			wx.MessageBox(_("هنالك قائمة  بهذا الإسم بالفعل"), _("خطأ"), style=wx.ICON_ERROR, parent=self)

	def ContextSetup(self):
		contextMenu = wx.Menu()
		rename = contextMenu.Append(-1, _("إعادة التسمية"))
		delete = contextMenu.Append(-1, _("حذف"))
		def popup():
			self.PopupMenu(contextMenu)
		self.playlistsList.Bind(wx.EVT_CONTEXT_MENU, lambda e:popup())
		self.Bind(wx.EVT_MENU, self.OnRename, rename)
		self.Bind(wx.EVT_MENU, self.OnDelete, delete)

	def OnRename(self, event):
		newName = input_box.Input(self, _("إعادة تسمية قائمة التشغيل"), _("قم بإدخال الإسم الجديد"))
		if newName.canceled: return
		os.rename(os.path.join(ppath, f"{self.playlistsList.StringSelection}.m3u"), os.path.join(ppath, f"{newName.text()}.m3u"))
		selection = self.playlistsList.Selection
		self.ListInit()
		self.playlistsList.Selection = selection

	def OnDelete(self, event):
		if self.playlistsList.Selection == -1: return
		ask = wx.MessageBox(_("هل أنت متأكد بأنك تريد حذف قائمة التشغيل {playlist}").format(playlist=self.playlistsList.StringSelection), _("تنبيه"), style=wx.YES_NO, parent=self)
		if ask == wx.YES:
			os.remove(os.path.join(ppath, f"{self.playlistsList.StringSelection}.m3u"))
			wx.MessageBox(_("تم حذف قائمة التشغيل بنجاح"), _("نجاح"))
		selection = self.playlistsList.Selection
		self.ListInit()
		try:
			self.playlistsList.Selection = selection-1
		except: pass

class playlist(wx.Dialog):
	def __init__(self, parent, ptname):
		super().__init__(parent, -1, title=ptname)
		self.p = wx.Panel(self)
		self.ptname = ptname
		self.content = {}
		self.tracks = wx.ListBox(self.p, -1)
		open = wx.Button(self.p, -1, _("فتح قائمة التشغيل: alt+o"), name="c")
		open.Bind(wx.EVT_BUTTON, self.OnOpen)
		open.SetDefault()
		up = wx.Button(self.p, -1, _("نقل إلى الأعلى: alt+u"), name="c")
		down = wx.Button(self.p, -1, _("نقل إلى الأسفل: alt+d"), name="c")
		up.Bind(wx.EVT_BUTTON, self.OnUp)
		down.Bind(wx.EVT_BUTTON, self.OnDown)
		remove = wx.Button(self.p, -1, _("حذف مِن قائمة التشغيل: alt+r"), name="c")
		remove.Bind(wx.EVT_BUTTON, self.OnRemove)
		add = wx.Button(self.p, -1, _("إضافة مقطع جديد إلى قائمة التشغيل: alt+a"))
		add.Bind(wx.EVT_BUTTON, self.OnAdd)
		close = wx.Button(self.p, wx.ID_CANCEL, _("إغلاق"))
		shortcuts = wx.AcceleratorTable((
			(wx.ACCEL_ALT, ord("A"), add.GetId()),
			(wx.ACCEL_ALT, ord("U"), up.GetId()),
			(wx.ACCEL_ALT, ord("D"), down.GetId()),
			(wx.ACCEL_ALT, ord("O"), open.GetId()),
			(wx.ACCEL_ALT, ord("R"), remove.GetId())
		))
		self.SetAcceleratorTable(shortcuts)
		self.get()
		self.Show()

	def OnRemove(self, evt):
		if not self.tracks.Strings: return
		ask = wx.MessageBox(_("هل أنت متأكد بأنك تريد حذف المقطع من قائمة التشغيل?"), _("تنبيه"), parent=self, style=wx.YES_NO)
		if ask == wx.YES:
			selection = self.tracks.Selection
			self.Parent.m.remove(self.ptname, self.tracks.Selection)
			self.get()
			if selection<self.tracks.Count-1: self.tracks.Selection = selection
			else: self.tracks.Selection = self.tracks.Count-1

	def OnOpen(self, evt):
		if not self.tracks.Strings: return
		try:
			g.player.media.stop()
			g.player.filename=""
			g.player.url=""
			g.player.startpoint=None
			g.player.endpoint=None
			g.player.repeate_some=False
			g.player=None
			g.player.LoadM3U(os.path.join(ppath, f"{self.ptname}.m3u"))
		except:
			g.filePath = ""
			g.folder_path=""
			g.tracks_list=[]
			g.playing_from_youtube=False
			g.player=media_player.Player(hwnd=self.Parent.Parent.GetHandle(), mu=True)
			g.player.LoadM3U(os.path.join(ppath, f"{self.ptname}.m3u"))
		for i in (self, self.Parent):
			i.Destroy()



	def OnUp(self, event):
		if not self.tracks.Strings: return
		if self.tracks.Selection == 0 : return speak(_("المقطع في بداية القائمة"))
		path = self.Parent.m.GetPath(self.ptname)
		self.Parent.m.move(path, self.tracks.Selection, "up")
		selection = self.tracks.Selection-1
		self.get()
		self.tracks.Selection = selection

	def OnDown(self, event):
		if not self.tracks.Strings: return
		if self.tracks.Selection == len(self.tracks.Strings)-1 : return speak(_("المقطع في نهاية القائمة"))
		path = self.Parent.m.GetPath(self.ptname)
		self.Parent.m.move(path, self.tracks.Selection, "down")
		selection = self.tracks.Selection+1
		self.get()
		self.tracks.Selection = selection

	def get(self):
		for i in self.p.GetChildren():
			i.Hide() if i.Name=="c" and i.Shown == True else None
		self.content = {}
		self.tracks.Clear()
		lst = self.Parent.m.GetContent(self.ptname)
		if not lst: return
		for i in self.p.GetChildren():
			i.Show() if i.Name=="c" and i.Shown == False else None
		index = 0
		for i in lst:
			self.content[index] = {"name":os.path.splitext(os.path.basename(i))[0], "path":i}
			self.tracks.Append(os.path.splitext(os.path.basename(i))[0])
			index +=1
		try:
			self.tracks.Selection = 0
		except: pass


	def OnAdd(self, event):
		fp = wx.FileSelector(_("قم بإختيار ملف لإضافته لقائمة التشغيل"), parent=self)
		if not fp: return
		self.Parent.m.add(self.ptname, fp)
		self.get()

class PlaylistsManager:
	def __init__(self):
		self.lists = {}

	def initialize(self):
		list = os.listdir(ppath)
		playlistsDict = {}
		index = 0
		for i in list:
			if not self.IsValid(i): continue
			playlistsDict[index] = {"name":self.GetName(i), "path":self.GetPath(i)}
			index+=1
		self.lists = playlistsDict

	def add(self, pname, fp):
		path = os.path.join(ppath, f"{pname}.m3u")
		with open(path, "a", encoding="utf-8") as f:
			f.write(f"{fp}\n")
			speak(_("تم إضافة المقطع بنجاح"))

	def new(self, playlistName):
		if os.path.exists(os.path.join(ppath, playlistName)): return False
		with open(os.path.join(ppath, playlistName), "w", encoding="utf-8") as f:
			return True

	def remove(self, playlistName):
		try:
			os.remove(os.path.join(ppath, playlistName))
		except:
			return False

	def IsValid(self, fn):
		if os.path.splitext(fn)[1].lower() == ".m3u":
			return True
		return False


	def GetName(self, fn):
		return os.path.splitext(fn)[0]

	def GetPath(self, fn):
		return os.path.join(ppath, f"{fn}.m3u")

	def GetContent(self, pname):
		path = self.GetPath(pname)
		content = []
		with open(path, "r", encoding="utf-8") as f:
			for i in f.readlines():
				if not i.startswith("#"):
					content.append(i.strip())
		return content

	def move(self, path, index, direction):
		with open(path, "r", encoding="utf-8") as f:
			lines = f.readlines()    
			track = lines.pop(index)
			if direction == 'up':
				new_index = index -1
			elif direction == 'down':
				new_index = index +1
		lines.insert(new_index, track)    
		with open(path, "w", encoding="utf-8") as f:
			f.writelines(lines)

	def remove(self, list, index):
		with open(self.GetPath(list), "r", encoding="utf-8") as f:
			content = f.readlines()
		content.pop(index)
		with open(self.GetPath(list), "w", encoding="utf-8") as f:
			f.writelines(content)

class SelectPlaylist(wx.Dialog):
	def __init__(self, parent, path):
		wx.Dialog.__init__(self, parent, -1, _("قم بتحديد قائمة تشغيل"))
		p = wx.Panel(self)
		self.path = path
		print(path)
		wx.StaticText(p, -1, _("قم بتحديد قائمة تشغيل"))
		self.m = PlaylistsManager()
		self.lst = wx.ListBox(p, -1)
		self.new = wx.Button(p, -1, _("إنشاء قائمة تشغيل جديدة"))
		self.new.Bind(wx.EVT_BUTTON, self.OnNewlist)
		self.Bind(wx.EVT_CHAR_HOOK, self.shortcuts)
		self.ListInit()
		self.ShowModal()

	def ListInit(self):
		self.m.initialize()
		if not self.m.lists: return
		for i in self.m.lists:
			self.lst.Append(self.m.lists[i]["name"])
		self.lst.Selection = 0
	def OnNewlist(self, event):
		if not self.FindFocus() == self.new: return
		pl = input_box.Input(self, _("إنشاء قائمة تشغيل جديدة"), _("قم بإدخال اسم قائمة التشغيل الجديدة"))
		if pl.canceled or not pl.text(): return
		if self.m.new(f"{pl.text()}.m3u"):
			speak(_("تم إنشاء قائمة التشغيل {P} بنجاح").format(P=pl.text()))
			self.ListInit()
			self.lst.Selection = self.lst.FindString(pl.text())
		else:
			wx.MessageBox(_("هنالك قائمة  بهذا الإسم بالفعل"), _("خطأ"), style=wx.ICON_ERROR, parent=self)

	def OnClose(self, evt):
#		if not self.FindFocus() == self.close: return
		self.Destroy()

	def shortcuts(self, evt):
		key = evt.GetKeyCode()
		if key == wx.WXK_ESCAPE:
			self.OnClose(None)
		elif key == wx.WXK_RETURN and self.FindFocus() == self.lst:
			self.m.add(self.lst.StringSelection, self.path)
			self.Destroy()
		evt.Skip()