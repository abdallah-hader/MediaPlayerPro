import wx
import requests
from threading import Thread
from wx.lib.newevent import NewEvent
import os
import sys
import globals as g
from settingsconfig import get

ProgressChangedEvent, EVT_PROGRESS_CHANGED = NewEvent()
DownloadFinishedEvent, EVT_DOWNLOAD_FINISHED = NewEvent()


def lcfu(silent=True):
	current = float(open(os.path.join(g.path, "languages", get("language"), "lc_messages/version.txt"), "r").read())
	url = "http://blindgamers.net/mpp/languages.json"
	try:
		request=requests.get(url)
		if request.status_code !=200:
			wx.MessageBox(_("لم نتمكن من الوصول إلى خدمة التحديثات, قد تكون هناك مشكلة مؤقتة, أو مشكلة في الإتصال لديك, تأكد مِن الإتصال بالأنترنت ثم عاود مجددًا."), _("خطأ"), style=wx.ICON_ERROR, parent=wx.GetApp().GetTopWindow()) if not silent else None
			return
		info = request.json()
		if float(info[get("language")]["latest"])>current:
			ask = wx.MessageBox(_("تم إكتشاف هناك تحديث جديد للغة {lang} هل تريد التحديث الآن?").format(lang=get("language")), _("هناك تحديث جديد للغة"), style=wx.YES_NO)
			if ask == wx.YES:
				wx.CallAfter(DownloadLanguageUpdate, wx.GetApp().GetTopWindow(), info[get("language")]["url"], info[get("language")]["latest"])
		else:
			wx.MessageBox(_("لديك أحدث تحديث للغة"), _("لم يتم العثور على تحديث")) if not silent else None
	except requests.ConnectionError:
		wx.MessageBox(_("حدث خطأ أثناء محاولة الإتصال بخدمة التحديثات, يرجى المحاولة لاحقًا"), _("خطأ في الإتصال"), style=wx.ICON_ERROR, parent=wx.GetApp().GetTopWindow()) if not silent else None

class DownloadLanguageUpdate(wx.Dialog):
	def __init__(self, parent, url, newVersion):
		os.chdir	(g.path)
		self.path = os.path.join(g.path, "languages", get("language"), "lc_messages", "MediaPlayerPro.mo")
		self.newVersion = newVersion
		wx.Dialog.__init__(self, parent, title=_("يتم تحميل التحديثات"))
		p=wx.Panel(self)
		self.CenterOnParent()
		wx.StaticText(p, -1, _("حالة التحميل"))
		self.download_status=wx.TextCtrl(p, -1, style=wx.TE_READONLY|wx.HSCROLL)
		self.download_status.SetFocus()
		cancelButton = wx.Button(p, wx.ID_CANCEL, _("إيقاف التحميل"))
		self.ProgressBar=wx.Gauge(p, -1, range=100)
		self.ProgressBar.Bind(EVT_PROGRESS_CHANGED, self.onChanged)
		self.Bind(EVT_DOWNLOAD_FINISHED, self.onFinished)
		cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)
		Thread(target=self.updateDownload, args=[url]).start()
		self.download = True
		self.ShowModal()

	def updateDownload(self, url):
		name = os.path.join(self.path, url.split("/")[-1])
		try:
			with requests.get(url, stream=True) as r:
				if r.status_code != 200:
					self.errorAction()
					return
				size = r.headers.get("content-length")
				try:
					size = int(size)
				except TypeError:
					self.errorAction()
					return
				recieved = 0
				progress = 0
				with open(self.path, "wb") as file:
					for part in r.iter_content(1024):
						file.write(part)
						if not self.download:
							file.close()
							self.Destroy()
							return

						recieved += len(part)
						progress = int(
							(recieved/size)*100
						)
						wx.PostEvent(self.ProgressBar, ProgressChangedEvent(value=progress))
			wx.PostEvent(self, DownloadFinishedEvent(path=name))
		except requests.ConnectionError:
			self.errorAction()

	def errorAction(self):
		wx.MessageBox(_("حدث خطأ أثناء عملية التحديث ، يرجى المحاولة مرة أخرى في وقت لاحق."), _("خطأ"), style=wx.ICON_ERROR, parent=self)
		self.Destroy()
	def onChanged(self, event):
		self.ProgressBar.SetValue(event.value)
		self.download_status.SetValue(_("يتم تحميل التحديث {}").format(event.value)+"%")

	def onFinished(self, event):
		with open(os.path.join(g.path, "languages", get("language"), "lc_messages/version.txt"), "w") as f:
			f.write(str(self.newVersion))
		wx.MessageBox(_("تم تحميل التحديث بنجاح, انقر فوق موافق لإعادة تشغيل البرنامج وتطبيق التحديث الجديد للغة"), _("نجاح"), parent=self)
		try:
			g.player.media.stop()
		except: pass
		g.pathloop=False
		os.execl(sys.executable, sys.executable, *sys.argv)
	def onCancel(self, event):
		self.download = False
