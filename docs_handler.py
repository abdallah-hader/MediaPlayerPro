import wx
import os
from settingsconfig import get

def get_doc():
	lang=get("language")
	try:
		f=open(f"docs/help_{lang}.txt", "r", encoding="utf-8")
		help=f.read()
		f.close()
		return help
	except FileIxistsError:
		wx.MessageBox(_("تعذر العثور على ملف المساعدة"), _("خطأ"), style=wx.ICON_ERROR, parent=wx.GetApp().GetTopWindow())
		return False