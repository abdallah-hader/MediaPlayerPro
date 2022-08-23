import wx

class help(wx.Dialog):
	def __init__(self, parent, text):
		wx.Dialog.__init__(self, parent, id=-1, title=_("دليل الإستخدام"))
		p=wx.Panel(self)
		self.CenterOnParent()
		guide=wx.TextCtrl(p, -1, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.HSCROLL)
		guide.Value=text
		guide.SetFocus()
		close=wx.Button(p, -1, _("إغلاق"))
		close.Bind(wx.EVT_BUTTON, lambda event:self.Destroy())
		self.ShowModal()