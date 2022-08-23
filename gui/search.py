import wx
from pyperclip import copy
from scripts.Speak import speak
from scripts import media_player
import subprocess
import globals as g
from youtubesearchpython import VideosSearch

class YoutubeSearch:
	def __init__(self, query):
		self.query=query
		self.results={}
		self.count=1
		self.search=VideosSearch(self.query)
		self.ParseResults()

	def ParseResults(self):
		results=self.search.result()["result"]
		for result in results:
			self.results[self.count]={
				"type":result["type"],
				"title":result["title"],
				"url":result["link"],
				"duration":result.get("duration"),
				"views":result.get("videoCount"),
				"channel":{
					"name": result["channel"]["name"], 
					"url": f"https://www.youtube.com/channel/{result['channel']['id']}"}
			}
			if result["type"] == "video":
				self.results[self.count]["views"] = self.parse_views(result["viewCount"]["text"])
			else:
				self.results[self.count]["views"] = None
			self.count += 1

	def get_titles(self):
		titles = []
		for result, data  in self.results.items():
			title = [data['title']]
			if data["type"] == "video":
				title += [self.get_duration(data['duration']),
					_('بواسطة {b} ').format(b=data['channel']['name']),
					self.views_part(data['views'])]
			titles.append(", ".join([item for item in title if item != ""]))
		return titles

	def get_last_titles(self):
		titles = self.get_titles()
		return titles[len(titles)-self.new_videos:len(titles)]

	def get_title(self, number):
		return self.results[number+1]["title"]

	def get_url(self, number):
		return self.results[number+1]["url"]

	def get_channel(self, number):
		return self.results[number+1]["channel"]

	def load_more(self):
		try:
			self.search.next()
		except:
			return
		current = self.count
		self.ParseResults()
		self.new_videos = self.count-current
		return True

	def parse_views(self, string):
		try:
			string = string.replace(",", "")
		except AttributeError:
			return
		return string.replace("views", "")

	def get_views(self, number):
		return self.results[number+1]['views']

	def views_part(self, data):
		if data is not None:
			return _("عدد المشاهدات {}").format(data)
		else:
			return _("بث مباشر")

	def get_duration(self, data): # get the duration of the video
		if data is not None:
			return _("المدة: {}").format(g.time_formatting(data))
		else:
			return ""

class FolderSearch(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, title=_("البحث في المجلد"))
		self.CenterOnParent()
		p=wx.Panel(self)
		wx.StaticText(p, -1, _("كلمة البحث"))
		self.searchbox=wx.TextCtrl(p, -1)
		self.ResultLabel=wx.StaticText(p, -1, _("نتائج البحث"))
		self.ResultsList=wx.ListBox(p, -1)
		self.ResultLabel.Hide()
		self.ResultsList.Hide()
		self.Bind(wx.EVT_CHAR_HOOK, self.shortcuts)
		self.ResultsList.Bind(wx.EVT_CONTEXT_MENU, self.OnContext)
		search=wx.Button(p, -1, _("بحث"))
		search.Bind(wx.EVT_BUTTON, self.OnSearch)
		close=wx.Button(p, -1, _("إغلاق"))
		close.Bind(wx.EVT_BUTTON, lambda e: self.Destroy())
		self.SelectedResult=""
		self.Done=False
		self.Show()

	def OnSearch(self, event):
		if self.searchbox.Value=="":
			self.searchbox.SetFocus()
			return speak(_("قم بإدخال كلمة بحث أولا"))
		self.ResultsList.Clear()
		for track in g.tracks_list:
			if self.searchbox.Value in track:
				self.ResultsList.Append(track)
		count=len(self.ResultsList.GetStrings())
		if count<=0:
			wx.MessageBox(_("لم يتم العثور على نتائج مطابِقة لكلمة البحث هذه"), _("لا توجد نتائج"), parent=self, style=wx.ICON_ERROR)
			return [False, self.Destroy()]
		if count==1:
			rcount=_("نتيجة واحدة")
		elif count==2:
			rcount=_("نتيجتان")
		else:
			rcount=_("نتائج")
		self.ResultLabel.SetLabel(_("نتائج البحث عن {w}, هناك {rc} {rc2}").format(w=self.searchbox.Value, rc2=rcount, rc=len(self.ResultsList.GetStrings())))
		self.ResultLabel.Show()
		self.ResultsList.Show()
		self.ResultsList.SetFocus()

	def shortcuts(self, event):
		key=event.GetKeyCode()
		if key==wx.WXK_RETURN and self.FindFocus()==self.ResultsList:
			self.SelectedResult=self.ResultsList.GetStringSelection()
			g.index=g.tracks_list.index(self.SelectedResult)
			g.set_title(g.tracks_list[g.index])
			if g.player is None:
				g.player=MediaPlayer.Player(f"{g.folder_path}/{g.tracks_list[g.index]}", g.handle)
				return self.Destroy()
			g.player.set_media(f"{g.folder_path}/{g.tracks_list[g.index]}")
			g.player.media.play()
			self.Destroy()
		elif key==wx.WXK_ESCAPE: self.Destroy()
		event.Skip()

	def OnContext(self, event):
		menu=wx.Menu()
		openfolderpath=menu.Append(-1, _("فتح مسار الملف"))
		copyfolderpath=menu.Append(-1, _("نسخ مسار الملف"))
		fpath=f"{g.folder_path}/{self.ResultsList.GetStringSelection()}".replace("/", "\\")
		self.Bind(wx.EVT_MENU, lambda e:copy(fpath), copyfolderpath)
		self.Bind(wx.EVT_MENU, lambda e: subprocess.run(f"explorer /select, {fpath}"), openfolderpath)
		self.PopupMenu(menu)
