import wx
import os
from settingsconfig import datapath
import globals as g
import shelve
from scripts import media_player
from . import youtube
from scripts.Speak import speak



class historygui(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, id=-1, title=_("سجل البحث"))
		self.CenterOnParent()
		self.history={}
		self.p=wx.Panel(self)
		wx.StaticText(self.p, -1, _("التاريخ"))
		self.date=wx.Choice(self.p, -1)
		self.history_label=wx.StaticText(self.p, -1, _("نتائج البحث"), name="main")
		self.HistoryList=wx.ListBox(self.p, -1, name="main")
		self.delete_date=wx.Button(self.p, -1, _("حذف التاريخ المحدد"))
		self.delete_date.Bind(wx.EVT_BUTTON, self.OnDeleteDate)
		self.clear=wx.Button(self.p, -1, _("محو السجل"))
		self.clear.Bind(wx.EVT_BUTTON, self.OnClear)
		close=wx.Button(self.p, wx.ID_CANCEL, _("إغلاق"))
		self.Bind(wx.EVT_CHAR_HOOK, self.shortcuts)
		self.date.Bind(wx.EVT_CHOICE, self.OnDate)
		self.HistoryList.Bind(wx.EVT_CHAR_HOOK, self.shortcuts)
		self.load()
		self.ShowModal()

	def load(self):
		f=history()
		self.history=f.get_history()
		if self.history is None: return self.clear.Disable()
		for date in self.history.keys():
			self.date.Append(date)
		try:
			self.date.Selection=0
			self.OnDate(None)
		except: pass

	def OnDate(self, event):
		current=self.date.GetStringSelection()
		self.HistoryList.Set(self.history[current])
		try:
			self.HistoryList.Selection=0
		except: pass

	def OnClear(self, event):
		msg=wx.MessageBox(_("في حال تم الضغط فوق نعم, سيتم حذف سجل البحث بأكمله ولا يمكنك إسترجاعه مرةً أخرى, هل تريد الحذف؟"), _("تنبيه"), style=wx.YES_NO)
		if msg==wx.YES:
			f=history()
			f.clear()
			self.clear.Disable()
			self.delete_date.Disable()
			self.HistoryList.Clear()
			self.date.Clear()
			wx.MessageBox(_("لقد تم حذف جميع سجل البحث"), _("نجاح"))

	def OnDeleteDate(self, event):
		msg=wx.MessageBox(_("في حال تم الضغط فوق نعم, سيتم حذف التاريخ المحدد ولا يمكنك إسترجاعه مرةً أخرى, هل تريد الحذف؟"), _("تنبيه"), style=wx.YES_NO)
		if msg==wx.YES:
			f=history()
			f.remove_date(self.date.GetStringSelection())
			self.date.Delete(self.date.GetSelection())
			self.clear.Disable()
			if len(self.date.Strings)<1:
				self.delete_date.Disable()
				self.HistoryList.Clear()
			wx.MessageBox(_("لقد تم حذف التاريخ المحدد مِن سجل البحث"), _("نجاح"))

	def shortcuts(self, event):
		key=event.GetKeyCode()
		if key==wx.WXK_RETURN or key==wx.WXK_NUMPAD_ENTER:
			if not self.FindFocus()==self.HistoryList: return
			g.hy=self
			y = youtube.SearchDialog(self.Parent, self.HistoryList.GetStringSelection(), self)
		event.Skip()

class history:
	def __init__(self):
		self.path=f"{datapath}/history"

	def init_history(self):
		with shelve.open(self.path) as f:
			if not "dates" in f:
				f["dates"] = {}

	def new_date(self, date, data):
		with shelve.open(self.path) as f:
			dates=f["dates"]
			dates[date] = data
			f["dates"] = dates

	def add_to_date(self, date, query):
		self.init_history()
		with shelve.open(self.path) as f:
			dates=f["dates"]
			if date in dates:
				dates[date].append(query)
				f["dates"] = dates
			else:
				self.new_date(date, [query])

	def get_history(self):
		with shelve.open(self.path) as f:
			if not "dates" in f or f["dates"]=={}: return None
			return f["dates"]

	def clear(self):
		with shelve.open(self.path) as f:
			f["dates"] = {}

	def remove_date(self, date):
		with shelve.open(self.path) as f:
			dates=f["dates"]
			if date in dates:
				del dates[date]
			f["dates"] = dates