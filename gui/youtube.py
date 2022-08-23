import wx
import threading
import pyperclip
import globals as g
import pafy
from .import youtube
from .history import history
from scripts.web_browser import Open
from .search import YoutubeSearch
from scripts.Speak import speak
from scripts import media_player
from datetime import datetime
from settingsconfig import get


def get_url(url):
	pafy.set_api_key("AIzaSyCEXsh-68oxoE-pdWYEmaa8OwNoMsoFGJI")
	try:
		video=pafy.new(url)
	except ValueError:
		return wx.MessageBox(_("لقد أدخلت رابط غير صالح."), _("خطأ"), style=wx.ICON_ERROR, parent=wx.GetApp().GetTopWindow())
	best=video.getbestaudio()
	burl=best.url
	title=video.title
	info=_("""
		 يتم التشغيل مِن يوتيوب: {title}\n
		المشاهدات: {views}\n
		المالك: {author}\n
		عدد الإعجابات: {likes}\n
		الوصف: {description}
	""").format(title=video.title, author=video.author, views=video.viewcount, likes=video.likes, description=video.description)
	g.youtube_description = video.description
	return [burl, info, title, url]

class SearchDialog(wx.Dialog):
	def __init__(self, parent, search_word=None, from_history=False):
		wx.Dialog.__init__(self, parent, title=_("البحث في يوتيوب"))
		self.from_history=from_history
		self.p=wx.Panel(self)
		self.CenterOnParent()
		self.setup_context()
		wx.StaticText(self.p, -1, _("كلمة البحث"))
		self.query=wx.TextCtrl(self.p, -1, style=wx.TE_PROCESS_ENTER)
		wx.StaticText(self.p, -1, _("قائمة النتائج"), name="result")
		self.Results=wx.ListBox(self.p, -1, name="result")
		self.Results.Bind(wx.EVT_CHAR_HOOK, self.OnMenu)
		self.Results.Bind(wx.EVT_LISTBOX, self.listbox)
		self.LoadAll=wx.CheckBox(self.p, -1, _("تحميل جميع النتائج الحالية في قائمة"), name="result")
		close=wx.Button(self.p, -1, _("إغلاق"))
		close.Bind(wx.EVT_BUTTON, lambda e:self.Hide())
		self.Bind(wx.EVT_TEXT_ENTER, self.startsearch)
		self.Bind(wx.EVT_CHAR_HOOK, self.shortcuts)
		self.search=None
		if not search_word is None:
			g.search_window=self
			self.query.Value=search_word
			self.query.SetFocus()
			self.Show()
			self.startsearch(None)


	def startsearch(self, event):
		if self.query.Value=="": return
		self.Results.SetFocus()
		threading.Thread(target=self.searchyt, args=[self.query.Value]).start()

	def searchyt(self, query):
		speak(_("يتم البحث عن {q}").format(q=query))
		try:
			self.search=YoutubeSearch(query)
		except:
			wx.MessageBox(_("حدث خطأ أثناء محاولة البحث, قد تكون هناك مشكلة بالإتصال, إذا استمرت المشكلة بالظهور قم بمراسلة المطور لحل المشكلة"), _("خطأ"), parent=self, style=wx.ICON_ERROR)
			return
		titles = self.search.get_titles()
		speak(_("اكتمل تحميل النتائج"))
		self.Results.Set(titles)
		for i in self.p.GetChildren():
			i.Show() if i.Name=="result" and i.Shown==False else None
		try:
			self.Results.SetSelection(0)
		except: pass
		if get("history") and not self.from_history:
			date=datetime.now().strftime("%d/%m/%Y")
			h=history().add_to_date(date, self.query.Value)
		if self.from_history:
			try:
				g.hy.Destroy()
			except RuntimeError:
				pass
		self.query.Value=""


	def OnMenu(self, event):
		key=event.GetKeyCode()
		if key==wx.WXK_RETURN:
			if len(self.Results.Strings)<1: return
			index=self.Results.Selection
			g.youtube_url=self.search.get_url(index)
			data=youtube.get_url(g.youtube_url)
			try:
				link=data[0]
			except:
				return
			g.youtube_file_info=data[1]
			title=data[2]
			g.tracks_list=[]
			g.playing_from_youtube=True
			if self.LoadAll.Value==True:
				for track in range(len(self.Results.Strings)):
					g.tracks_list.append([self.search.get_title(track), self.search.get_url(track)])
			if g.player==None:
				g.player=MediaPlayer.Player(link, wx.GetApp().GetTopWindow().GetHandle())
				g.set_title(title)
				g.player.title=title
				g.player.url=g.youtube_url
				self.Hide()
				wx.GetApp().GetTopWindow().SetFocus()
				return
			try:
				g.player.media.stop()
			except: pass
			g.player.set_media(link)
			g.playing_from_youtube=True
			g.set_title(title)
			g.player.title=title
			g.player.url=g.youtube_url
#			g.tracks_list=[]
			g.folder_path=""
			g.player.media.play()
			self.Hide()
			wx.GetApp().GetTopWindow().SetFocus()
		event.Skip()

	def listbox(self, event):
		if self.Results.Strings==[]:
			return
		if self.Results.Selection==len(self.Results.Strings)-1:
			speak(_("يتم تحميل المزيد من النتائج"))
			if self.search.load_more() is None:
				return speak(_("لا توجد نتائج أُخرى"))
			threading.Thread(target=self.load_more).start()
			speak(_("تم تحميل المزيد من النتائج"))

	def load_more(self):
		self.Results.Append(self.search.get_last_titles())

	def shortcuts(self, event):
		key=event.GetKeyCode()
		if key==wx.WXK_ESCAPE:
			self.Hide()
			wx.GetApp().GetTopWindow().SetFocus()
		event.Skip()

	def setup_context(self):
		self.context=wx.Menu()
		open_in_browser=self.context.Append(-1, _("فتح الفيديو في المتصفح\tv"))
		open_channel_in_browser=self.context.Append(-1, _("فتح القناة في المتصفح\tc"))
		copy_video_link=self.context.Append(-1, _("نسخ رابط الفيديو\tu"))
		copy_channel_link=self.context.Append(-1, _("نسخ رابط القناة\tl"))
		self.Bind(wx.EVT_MENU, self.OpenVideoInBrowser, open_in_browser)
		self.Bind(wx.EVT_MENU, self.OpenChannelInBrowser, open_channel_in_browser)
		self.Bind(wx.EVT_MENU, lambda e: pyperclip.copy(self.search.get_url(self.Results.Selection)), copy_video_link)
		self.Bind(wx.EVT_MENU, lambda e: pyperclip.copy(self.search.get_channel(self.Results.Selection)["url"]), copy_channel_link)
		def popup():
			if len(self.Results.Strings)>1 and self.FindFocus()==self.Results and not self.Results.Selection==-1:
				self.PopupMenu(self.context)
		self.Bind(wx.EVT_CONTEXT_MENU, lambda e:popup())

	def OpenVideoInBrowser(self, event):
		speak(_("يتم الفتح في المتصفح"))
		Open(self.search.get_url(self.Results.Selection))

	def OpenChannelInBrowser(self, event):
		speak(_("يتم الفتح في المتصفح"))
		Open(self.search.get_channel(self.Results.Selection)["url"])