import wx
import os
from settingsconfig import datapath
import globals as g
from scripts import media_player
from . import youtube
from scripts.Speak import speak
from . import input_box
import shelve


class favoritegui(wx.Dialog):
#the dialog of favorite class
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, id=-1, title=_("المفضلة"))
		self.CenterOnParent()
		self.favorites={}
		self.p=wx.Panel(self)
		wx.StaticText(self.p, -1, _("الفئات"))
		self.categorys=wx.Choice(self.p, -1)
		self.categorys.Bind(wx.EVT_CHOICE, self.OnCategorys)
		wx.StaticText(self.p, -1, _("قائمة المفضلة"), name="main")
		self.FavoriteList=wx.ListBox(self.p, -1, name="main")
		self.Bind(wx.EVT_CHAR_HOOK, self.shortcuts)
		OpenAll=wx.Button(self.p, -1, _("فتح جميع العناصر كقائمة"))
		OpenAll.Bind(wx.EVT_BUTTON, self.OnOpenAll)
		AddCategory=wx.Button(self.p, -1, _("إضافة فئة جديدة"))
		AddCategory.Bind(wx.EVT_BUTTON, self.OnAddCategory)
		self.clear=wx.Button(self.p, -1, _("حذف الفئة"))
		self.clear.Bind(wx.EVT_BUTTON, self.OnClear)
		close=wx.Button(self.p, -1, _("إغلاق"))
		close.Bind(wx.EVT_BUTTON, lambda e:self.Destroy())
		f=favorite().init_favorite()
		self.load()
		self.ShowModal()

	def load(self):
		f=favorite()
		self.favorites=f.get_favorites()
		if self.favorites is None: return self.clear.Disable()
		for index in self.favorites.keys():
			self.categorys.Append(index)
		try:
			self.categorys.Selection=0
			self.OnCategorys(None)
		except Exception as e: print(e)

	def OnCategorys(self, event):
		if self.categorys.Selection==-1: return
		cate=self.favorites[self.categorys.GetStringSelection()]
		self.FavoriteList.Set([i for i in cate])
		try:
			self.FavoriteList.Selection=0
		except: pass

	def OnClear(self, event):
		msg=wx.MessageBox(_("في حال تم الضغط فوق نعم, سيتم حذف الفئة {c} مع العناصر في داخل هذه الفئة, هل تريد الحذف؟").format(c=self.categorys.GetStringSelection()), _("تنبيه"), style=wx.YES_NO)
		if msg==wx.YES:
			f=favorite()
			f.DelCategory(self.categorys.GetStringSelection())
			selection=self.categorys.Selection
			self.categorys.Delete(selection)
			self.FavoriteList.Clear()
			try:
				self.categorys.Selection=selection
				self.OnCategorys(None)
			except:
				self.FavoriteList.Clear()
				self.clear.Disable()
			wx.MessageBox(_("لقد تم حذف الفئة بنجاح"), _("نجاح"))

	def get_selection(self):
		return self.favorites[self.categorys.GetStringSelection()][self.FavoriteList.GetStringSelection()]

	def OnAddCategory(self, event):
		f=favorite()
		c=input_box.Input(self, _("الإسم"), _("قم بإدخال إسم الفئة المراد إضافتها"))
		if c.canceled: return
		f.AddCategory(c.text())

	def OnOpenAll(self, event):
		if len(self.FavoriteList.Strings)<1: return
		g.tracks_list=[]
		for track in self.FavoriteList.Strings:
			index = self.favorites[self.categorys.GetStringSelection()][track]
			g.tracks_list.append(index["path"])
		g.FavoriteLoaded = True
		self.play()

	def shortcuts(self, event):
		key=event.GetKeyCode()
		if key==wx.WXK_ESCAPE:
			self.Destroy()
		elif key==wx.WXK_F1:
			if self.FavoriteList.Selection==-1: return
			speak(_("{t}, يبدأ المقطع عند ({p}), النوع ({iu}), تم الإضافة في ({time}).").format(t=self.FavoriteList.GetStringSelection(), p=self.favorites[self.categorys.GetStringSelection()][self.FavoriteList.GetStringSelection()]["elapsed"], time=self.favorites[self.categorys.GetStringSelection()][self.FavoriteList.GetStringSelection()]["added_time"], iu=_("ملف") if not self.favorites[self.categorys.GetStringSelection()][self.FavoriteList.GetStringSelection()]["is_url"] else _("رابط")))
		elif key==wx.WXK_DELETE or key==wx.WXK_NUMPAD_DELETE and self.FindFocus()==self.FavoriteList:
			if self.FavoriteList.Selection==-1 : return
			selection=self.FavoriteList.Selection
			index = self.get_selection()
			msg=wx.MessageBox(_("هل تريد إزالة {t} مِن المفضلة?").format(t=index["title"]), _("حذف"), style=wx.YES_NO, parent=self)
			if msg==wx.YES:
				f=favorite()
				f.delete_favorite(self.categorys.GetStringSelection() ,index["title"])
				self.favorites=f.get_favorites()
				self.FavoriteList.Delete(selection)
				try:
					self.FavoriteList.Selection=Selection
				except:
					pass
		elif key==wx.WXK_RETURN or key==wx.WXK_NUMPAD_ENTER and self.FindFocus()==self.FavoriteList:
			if len(self.FavoriteList.Strings)<1: return
			g.tracks_list=[]
			self.play()
		event.Skip()

	def play(self):
		index=self.get_selection()
		if index["is_url"]:
			g.youtube_url=index["url"]
			data=youtube.get_url(g.youtube_url)
			try:
				link=data[0]
				title=data[2]
			except: return
			g.youtube_file_info=data[1]
			g.playing_from_youtube=True
			if g.player==None:
				g.player=media_player.Player(link, wx.GetApp().GetTopWindow().GetHandle())
				g.set_title(title)
				g.player.title=title
				g.player.url=g.youtube_url
				g.player.media.set_position(float(index["position"]))
				self.Destroy()
				return
			try:
				g.player.media.stop()
			except: pass
			g.player.set_media(link)
			g.playing_from_youtube=True
			g.set_title(title)
			g.player.filename=title
			g.player.url=g.youtube_url
			g.player.media.play()
			g.player.media.set_position(float(index["position"]))
			return self.Destroy()
		g.set_title(index["title"])
		if g.player is None:
			g.player=MediaPlayer.Player(index["path"], g.handle)
			g.player.media.set_position(float(index["position"]))
			return self.Destroy()
		g.player.set_media(index["path"])
		g.player.media.play()
		g.player.media.set_position(float(index["position"]))
		self.Destroy()

class AddFavorite(wx.Dialog):
# the add favorite dialog class
	def __init__(self, parent, name, info):
		wx.Dialog.__init__(self, parent, title=_("إضافة {t} إلى المفضلة").format(t=name))
		p=wx.Panel(self)
		self.Center()
		self.info=info
		self.name=name
		wx.StaticText(p, -1, _("اختر الفئة"))
		self.category=wx.Choice(p, -1)
		wx.StaticText(p, -1, _("الإسم"))
		self.NameField=wx.TextCtrl(p, -1, value=self.name)
		add=wx.Button(p, -1, _("إضافة"))
		add_category=wx.Button(p, -1, _("إضافة فئة جديدة"))
		add_category.Bind(wx.EVT_BUTTON, self.OnAddCategory)
		cancel = wx.Button(p, wx.ID_CANCEL, _("إلغاء"))
		add.Bind(wx.EVT_BUTTON, self.OnAdd)
		self.f=favorite()
		self.f.init_favorite()
		favorites=self.f.get_favorites()
		if not favorites==None:
			for index in favorites.keys():
				self.category.Append(index)
		else:
			msg=wx.MessageBox(_("لا توجد هناك فئات متوفرة, يبدو تم حذف جميع الفئات مع الفئة الإفتراضية )الفئة الإفتراضية(, في حال لا يوجد هناك أي فئة متوفرة, لا يمكن إضافة عناصر للمفضلة, هل تريد إنشاء فئة الآن?"), _("لم يتم العثور على فئات"), style=wx.YES_NO, parent=self)
			if msg==wx.YES:
				c=input_box.Input(self, _("الإسم"), _("قم بإدخال إسم الفئة المراد إضافتها"))
				if c.canceled: return self.Destroy()
				self.f.AddCategory(c.text())
				self.category.Append(c.text())
			else:
				return self.Destroy()
		try:
			self.category.Selection=0
		except: pass
		self.ShowModal()

	def OnAdd(self, event):
		if self.category.Selection==-1: return
		if not self.info["title"] == self.NameField.Value : self.info["title"] = self.NameField.Value
		self.f.add(self.category.GetStringSelection(), self.NameField.Value, self.info)
		self.Destroy()

	def OnAddCategory(self, event):
		c=input_box.Input(self, _("الإسم"), _("قم بإدخال إسم الفئة المراد إضافتها"))
		if c.canceled: return self.Destroy()
		self.f.AddCategory(c.text())
		self.category.Clear()
		favorites=self.f.get_favorites()
		if not favorites==None:
			for index in favorites.keys():
				self.category.Append(index)
		try:
			self.category.SetSelection(len(self.category.Strings)-1)
		except:
			self.category.Selection=0
class favorite:
	def __init__(self):
		self.path=f"{datapath}/favorites"

	def init_favorite(self):
		with shelve.open(self.path) as f:
			if not "favorite" in f:
				f["favorite"] = {_("الفئة الإفتراضية"):{}}

	def add(self, category, title, data):
		with shelve.open(self.path) as f:
			favorites=f["favorite"]
			favorites[category][title] = data
			f["favorite"] = favorites
			speak(_("تم الإضافة إلى المفضلة"))

	def get_favorites(self):
		with shelve.open(self.path) as f:
			if len(f["favorite"])<1 or not "favorite" in f: return None
			index=0
			data=f["favorite"]
			return data

	def AddCategory(self, category):
		with shelve.open(self.path) as f:
			data=f["favorite"]
			data[category] = {}
			f["favorite"] = data
			speak(_("تم إضافة الفئة بنجاح"))

	def DelCategory(self, category):
		with shelve.open(self.path) as f:
			data=f["favorite"]
			del data[category]
			f["favorite"] = data

	def delete_favorite(self, category, i):
		with shelve.open(self.path) as f:
			data=f["favorite"]
			del data[category][i]
			f["favorite"] = data