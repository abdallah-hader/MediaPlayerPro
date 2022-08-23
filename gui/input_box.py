import wx
from scripts.Speak import speak

class Input(wx.Dialog):
	def __init__(self, parent, title, message, num=False, Min=0, Max=0, position=0):
		wx.Dialog.__init__(self, parent, id=-1, title=title)
		p=wx.Panel(self)
		wx.StaticText(p, -1, message)
		if not num:
			self.txt=wx.TextCtrl(p, -1)
		elif num:
			self.txt=wx.SpinCtrl(p, -1, min=Min, max=Max)
			self.txt.Value=position
		self.CenterOnParent()
		self.txt.SetFocus()
		self.canceled=False
		self.ok=wx.Button(p, wx.ID_OK)
		self.cancel=wx.Button(p, -1, _("إلغاء"))
		self.ok.SetLabel(_("موافق"))
		self.cancel.Bind(wx.EVT_BUTTON, self.OnCancel)
		self.Bind(wx.EVT_CHAR_HOOK, self.OnEscape)
		self.ok.SetDefault()
		self.ShowModal()

	def text(self):
		return self.txt.Value

	def OnCancel(self, event):
		speak(_("تم الإلغاء"))
		self.canceled=True
		self.Destroy()

	def OnEscape(self,event):
		k=event.GetKeyCode()
		if k==wx.WXK_ESCAPE:
			self.OnCancel(None)
		event.Skip()

