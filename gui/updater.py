import requests
import wx
from threading import Thread
from wx.lib.newevent import NewEvent
import os
import json
#from accessible_output2 import outputs
import application
from settingsconfig import get
import shutil
import subprocess
import sys
import globals as g


ProgressChangedEvent, EVT_PROGRESS_CHANGED = NewEvent()
DownloadFinishedEvent, EVT_DOWNLOAD_FINISHED = NewEvent()
update_path=os.path.join(os.getenv("appdata"), "Media Player Pro/updates")

def GetLang():
	if get("language")=="ar":
		return 0
	elif get("language")=="en":
		return 1
	else:
		return 1

def cfu(silent=False):
	url="http://blindgamers.net/mpp/update.json"
	try:
		request=requests.get(url)
		if request.status_code !=200:
			wx.MessageBox(_("لم نتمكن من الوصول إلى خدمة التحديثات, قد تكون هناك مشكلة مؤقتة, أو مشكلة في الإتصال لديك, تأكد مِن الإتصال بالأنترنت ثم عاود مجددًا."), _("خطأ"), style=wx.ICON_ERROR, parent=wx.GetApp().GetTopWindow()) if not silent else None
			return
		info = request.json()
		if info["version"]>application.version:
			ask=wx.MessageBox(_("هناك تحديث جديد {name} الإصدار {ver} هل تريد التحديث الآن؟").format(ver=info["version"], name=application.name), _("تم العثور على تحديث جديد"), style=wx.YES_NO, parent=wx.GetApp().GetTopWindow())
			if ask==wx.YES:
				wx.CallAfter(DownloadUpdate, wx.GetApp().GetTopWindow(), info["url"])
		else:
			wx.MessageBox(_("لديك أحدث إصدار مِن MediaPlayerPro"), _("لم يتم العثور على تحديثات"), parent=wx.GetApp().GetTopWindow()) if not silent else None
	except requests.ConnectionError:
		wx.MessageBox(_("حدث خطأ أثناء محاولة الإتصال بخدمة التحديثات, يرجى المحاولة لاحقًا"), _("خطأ في الإتصال"), style=wx.ICON_ERROR, parent=wx.GetApp().GetTopWindow()) if not silent else None


class DownloadUpdate(wx.Dialog):
	def __init__(self, parent, url):
		wx.Dialog.__init__(self, parent, title=_("يتم تحميل التحديثات"))
		p=wx.Panel(self)
		self.Center()
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
		if os.path.exists(update_path):
			shutil.rmtree(update_path)
		os.mkdir(update_path)
		name = os.path.join(update_path, url.split("/")[-1])
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
				with open(name, "wb") as file:
					for part in r.iter_content(1024):
						file.write(part)
						if not self.download:
							file.close()
							shutil.rmtree(update_path)
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
		shutil.rmtree(update_path)
		self.Destroy()
	def onChanged(self, event):
		self.ProgressBar.SetValue(event.value)
		self.download_status.SetValue(_("يتم تحميل التحديث {}").format(event.value)+"%")

	def onFinished(self, event):
		wx.MessageBox(_("تم تحميل التحديث بنجاح, انقر فوق موافق لِتبدأ عملية التثبيت."), _("نجاح"), parent=self)
		try:
			g.player.media.stop()
		except: pass
		g.pathloop=False
		try:
			self.download_status.Value = _("يتم تثبيت التحديث")
			path = os.path.join(update_path, event.path)
			subprocess.Popen('"{}" /silent'.format(path), shell=True)
		except:
			wx.MessageBox(_("حدث خطأ غير متوقع عند محاولة فتح الملف للتثبيت، أعد تنزيل التحديث مرة أخرى، وإذا استمرت المشكلة، فقم بالإتصال بالمطور لحلها"), _("خطأ"), style=wx.ICON_ERROR, parent=self)
			self.Destroy()
			return
		sys.exit()
	def onCancel(self, event):
		self.download = False
