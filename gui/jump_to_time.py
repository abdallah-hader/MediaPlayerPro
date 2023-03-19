import wx
import globals as g
import datetime
from settingsconfig import get
from scripts.Speak import speak

class Jump(wx.Dialog):
	def __init__(self, parent):
		super().__init__(parent, -1, _("الإنتقال إلى الوقت"))
		if not g.player: return
		p = wx.Panel(self)
		self.timeHour = self.timeMinute = self.timeSecond = 0
		wx.StaticText(p, -1, _("ساعة"))
		self.hour = wx.TextCtrl(p, -1)
		self.hour.Bind(wx.EVT_KEY_DOWN, self.OnHourChange)
		wx.StaticText(p, -1, _("دقيقة"))
		self.minute = wx.TextCtrl(p, -1)
		self.minute.Bind(wx.EVT_KEY_DOWN, self.OnChangeMinute)
		wx.StaticText(p, -1, _("ثانية"))
		self.second = wx.TextCtrl(p, -1)
		self.second.Bind(wx.EVT_KEY_DOWN, self.OnChangeSecond)
		ok = wx.Button(p, -1, _("موافق"))
		ok.Bind(wx.EVT_BUTTON, self.OnOk)
		ok.SetDefault()
		cancel = wx.Button(p, wx.ID_CANCEL, _("إلغاء"))
		duration = g.player.get_duration(1).split(":")
		self.timeHour = duration[0]
		self.timeMinute = duration[1]
		self.timeSecond = duration[2]
		if self.timeHour =="0": self.hour.Hide()
		if self.timeMinute == "0": self.minute.Hide()
		if self.timeSecond=="0": self.second.Hide()
		self.hour.Value = self.timeHour
		self.minute.Value = self.timeMinute
		self.second.Value = self.timeSecond
		self.Show()

	def OnOk(self, event):
		timeSTR = f"{self.hour.Value}:{self.minute.Value}:{self.second.Value}"
		time_parts = [int(part) for part in timeSTR.split(':')]
		jump_time = datetime.timedelta(hours=time_parts[0], minutes=time_parts[1], seconds=time_parts[2])
		if int(jump_time.total_seconds() * 1000) > g.player.media.get_length(): return speak(_("لقد أدخلت وقت أكبر من وقت الملف"))
		g.player.media.set_time(int(jump_time.total_seconds() * 1000))
		speak(f"{g.player.get_elapsed()}") if get("speakfr") else None

	def OnChangeMinute(self, event):
		if event.GetKeyCode() == wx.WXK_UP:
			current = self.minute.Value
			if current == self.timeMinute: return
			new = 0
			if len(current) ==1 :
				new = int(current)+1
			else:
				if current[0] == "0":
					if current[1]=="9": new = 10
					else: new = f"{current[0]}{int(current[1])+1}"
				else: new = int(current)+1
			self.minute.Value = str(new)
		if event.GetKeyCode() == wx.WXK_DOWN:
			if self.minute.Value == "0" or self.minute.Value == "00": self.minute.Value = self.timeMinute
			current = self.minute.Value
			new = 0
			if len(current) ==1 :
				new = int(current)-1
			else:
				if current[0] == "0":
					if current[1]=="0" or current=="0": new = self.timeMinute
					else: new = f"{current[0]}{int(current[1])-1}"
				else: new = int(current)-1
			self.minute.Value = str(new)
		event.Skip()

	def OnChangeSecond(self, event):
		if event.GetKeyCode() == wx.WXK_UP:
			current = self.second.Value
			if current == self.timeSecond: return
			new = 0
			if len(current) ==1 :
				new = int(current)+1
			else:
				if current[0] == "0":
					if current[1]=="9": new = 10
					else: new = f"{current[0]}{int(current[1])+1}"
				else: new = int(current)+1
			self.second.Value = str(new)
		if event.GetKeyCode() == wx.WXK_DOWN:
			if self.second.Value == "0" or self.second.Value == "00": self.second.Value = self.timeSecond
			current = self.second.Value
			new = 0
			if len(current) ==1 :
				new = int(current)-1
			else:
				if current[0] == "0":
					if current[1]=="0": new = self.timeSecond
					else: new = f"{current[0]}{int(current[1])-1}"
				else: new = int(current)-1
			self.second.Value = str(new)
		event.Skip()

	def OnHourChange(self, event):
		if event.GetKeyCode() == wx.WXK_UP:
			current = self.hour.Value
			if current == self.timeHour: return
			new = 0
			if len(current) ==1 :
				new = int(current)+1
			else:
				if current[0] == "0":
					if current[1]=="9": new = 10
					else: new = f"{current[0]}{int(current[1])+1}"
				else: new = int(current)+1
			self.hour.Value = str(new)
		if event.GetKeyCode() == wx.WXK_DOWN:
			if self.hour.Value == "0" or self.hour.Value == "00": self.hour.Value = self.timeHour
			current = self.hour.Value
			new = 0
			if len(current) ==1 :
				new = int(current)-1
			else:
				if current[0] == "0":
					if current[1]=="0": new = self.timeHour
					else: new = f"{current[0]}{int(current[1])-1}"
				else: new = int(current)-1
			self.hour.Value = str(new)
		event.Skip()