from time import sleep
import threading
import wx
import youtubesearchpython as yt
import pyperclip
from scripts.Speak import speak

class comments(wx.Dialog):
	def __init__(self, parent, url):
		wx.Dialog.__init__(self, parent, title=_("التعليقات"))
		p=wx.Panel(self)
		self.Bind(wx.EVT_CHAR_HOOK, self.shortcuts)
		self.CenterOnParent()
		wx.StaticText(p, -1, _("قائمة التعليقات"))
		self.CommentsList=wx.ListBox(p, -1)
		self.CommentsList.Bind(wx.EVT_LISTBOX, self.load)
		wx.StaticText(p, -1, _("نص التعليق"))
		self.comment_text=wx.TextCtrl(p, -1, style=wx.TE_MULTILINE|wx.HSCROLL)
		copy=wx.Button(p, -1, _("نسخ التعليق"))
		copy.Bind(wx.EVT_BUTTON, lambda e:pyperclip.copy(str(self.CommentsList.GetStringSelection())) if self.CommentsList.Selection!=-0 else None)
		close=wx.Button(p, -1, _("إغلاق"))
		self.video_id = url
		self.comments = None
		self.count=1
		self.commentslist=[]
		self.get()
		close.Bind(wx.EVT_BUTTON, self.close)
		self.Bind(wx.EVT_CLOSE, self.close)
		self.Show()

	def add(self):
		c=self.comments.comments['result']
		for i in c:
			comm=_("{content}, المُعلق: {author}, {published}").format(author=i["author"]["name"], content=i["content"], published=self.get_time(i["published"]))
			self.commentslist.append(comm)
		for i in self.commentslist:
			self.CommentsList.Append(i) if i not in self.CommentsList.GetStrings() else None
			self.count+=1
		try:
			self.CommentsList.Selection=0
		except: pass


	def get(self):
		try:
			self.comments=yt.Comments(self.video_id)
		except:
			wx.MessageBox(_("لا تتوفر تعليقات لِهذا الفيديو"), _("تنبيه"), parent=self)
			self.Destroy()
		self.add()

	def load(self, event):
		try:
			self.comment_text.Value=self.CommentsList.GetStringSelection()
		except:
			pass
		if self.CommentsList.Selection==len(self.CommentsList.Strings)-1:
			if self.comments.hasMoreComments:
				speak(_("يتم تحميل المزيد من التعليقات"))
				self.comments.getNextComments()
			else: return speak(_("لا يوجد هناك المزيد من التعليقات"))
			c=self.comments.comments['result']
			for i in c[self.count::]:
				comm=_("{content}, المُعلق: {author}, {published}").format(author=i["author"]["name"], content=i["content"], published=self.get_time(i["published"]))
				self.count+=1
				self.CommentsList.Append(comm)
			speak(_("اكتمل تحميل المزيد من التعليقات"))

	def shortcuts(self, event):
		key=event.GetKeyCode()
		if key==wx.WXK_ESCAPE:
			self.close(None)
		event.Skip()

	def get_time(self, time):
		time=time.split(" ")
		tt=""
		if time[1]=="months": tt=_("أشهر")
		elif time[1]=="month": tt=_("شهر")
		elif time[1]=="day":tt=_("يوم")
		elif time[1]=="days":tt=_("أيام")
		elif time[1]=="week": tt=_("إسبوع")
		elif time[1]=="weeks": tt=_("أسابيع")
		elif time[1]=="year":tt=_("سنة")
		elif time[1]=="years":tt=_("سنين")
		else: tt=time[1]
		return _("منذ {t1} {t2}").format(t1=time[0], t2=tt)

	def close(self, event):
		self.comments.comments['result']=[]
		self.Destroy()

