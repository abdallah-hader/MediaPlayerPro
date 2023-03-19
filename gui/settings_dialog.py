import wx
import os
from settingsconfig import get, new, spath
import sys, zipfile
from language import supported_languages
from scripts.Speak import speak
from threading import Thread
import globals as g
from datetime import datetime

languages = {index:language for language, index in enumerate(supported_languages.values())}

class settingsgui(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, -1, title=_("إعدادات البرنامج"))
		self.CenterOnParent()
		p=wx.Panel(self)
		wx.StaticText(p, -1, _("اختر ما تريد تعديله من الإعدادات"))
		tab1=wx.Listbook(p, -1)
		self.general_settings=GeneralSettings(tab1)
		tab1.AddPage(self.general_settings, _("الإعدادات العامة"))
		self.speak_settings=SpeakSettings(tab1)
		tab1.AddPage(self.speak_settings, _("إعدادات النطق"))
		self.subtitles=subtitles(tab1)
		tab1.AddPage(self.subtitles, _("إعدادات الترجمات"))
		self.hotkeys=HotKeys(tab1)
		tab1.AddPage(self.hotkeys, _("إعدادات الإختصارات العامة"))
		self.backup = backup(tab1)
		tab1.AddPage(self.backup, _("النسخ الأحتياطي والإستعادة"))
		ok=wx.Button(p, -1, _("حفظ الإعدادات"))
		ok.Bind(wx.EVT_BUTTON, self.OnOk)
		ok.SetDefault()
		cancel=wx.Button(p, wx.ID_CANCEL, _("إلغاء"))
		self.ShowModal()

	def OnOk(self, event):
		restart= False
		lang=self.general_settings.lang.GetStringSelection()
		key=""
		if self.hotkeys.control.Value==True:
			key=key+"control"
		if self.hotkeys.shift.Value==True:
			key=key+"shift"
		if self.hotkeys.alt.Value==True:
			key=key+"alt"
		if self.hotkeys.win.Value==True:
			key=key+"win"
		if not get("check_for_updates_at_startup") == self.general_settings.CFU.GetValue():
			new("check_for_updates_at_startup", self.general_settings.CFU.GetValue())
		if not get("languageupdates") == self.general_settings.LCFU.GetValue():
			new("languageupdates", self.general_settings.LCFU.GetValue())
		if not get("save_at_exit") == self.general_settings.SaveLast.GetValue():
			new("save_at_exit", self.general_settings.SaveLast.GetValue())
		if not get("load_first_file")==self.general_settings.load_first_file.GetValue():
			new("load_first_file", self.general_settings.load_first_file.GetValue())
		if not get("load_directory_file") == self.general_settings.load_directory_file.GetValue():
			new("load_directory_file", self.general_settings.load_directory_file.GetValue())
		if not get("history") == self.general_settings.history.GetValue():
			new("history", self.general_settings.history.GetValue())
		if not int(get("seek"))==int(self.general_settings.seek.Value):
			new("seek", self.general_settings.seek.Value)
		if not get("speakv") ==self.speak_settings.speak_volume.GetValue():
			new("speakv", self.speak_settings.speak_volume.GetValue())
		if not get("speakfr") == self.speak_settings.speak_fr.GetValue():
			new("speakfr", self.speak_settings.speak_fr.GetValue())
		if not get("speak_play_pause")==self.speak_settings.speak_pause.GetValue():
			new("speak_play_pause", self.speak_settings.speak_pause.GetValue())
		if not get("speakspeedrate")==self.speak_settings.speakspeedrate.GetValue():
			new("speakspeedrate", self.speak_settings.speakspeedrate.GetValue())
		if not get("speakreplayed")==self.speak_settings.speakreplayed.GetValue():
			new("speakreplayed", self.speak_settings.speakreplayed.GetValue())
		lang = {value:key for key, value in languages.items()}
		if not get("hotkeys", section="keybord")==key:
			new("hotkeys", key, section="keybord")
			restart=True
		if not get("replace_pages", section="keybord")==self.hotkeys.replace_pages.GetValue():
			new("replace_pages", self.hotkeys.replace_pages.GetValue(), section="keybord")
			restart=True
		if not lang[self.general_settings.lang.Selection] == get("language"):
			new("language", lang[self.general_settings.lang.Selection])
			restart=True
		if not int(get("volume", "subtitles")) == self.subtitles.volume.Selection+1:
			new("volume", self.subtitles.volume.Selection+1, "subtitles")
			try:
				g.sapi.set_volume(self.subtitles.volume.Selection+1)
			except: pass
		if not int(get("voice", "subtitles")) == self.subtitles.voice.Selection:
			new("voice", self.subtitles.voice.Selection, "subtitles")
			try:
				g.sapi.set_voice(self.subtitles.voice.Selection)
			except: pass
		if not int(get("speed", "subtitles")) == self.subtitles.speed_choice.Selection:
			new("speed", self.subtitles.speed_choice.Selection, "subtitles")
			try:
				g.sapi.set_speed(self.subtitles.speed_choice.Selection)
			except: pass
		if not get("sapi", "subtitles") == self.subtitles.sapi.Value:
			new("sapi", self.subtitles.sapi.Value, "subtitles")
		if not get("autodetect", "subtitles") == self.subtitles.AutoDetect.Value:
			new("autodetect", self.subtitles.AutoDetect.Value, "subtitles")
		if not get("read", "subtitles") == self.subtitles.read.Value:
			new("read", self.subtitles.read.Value, "subtitles")
		if restart==True:
			msg = wx.MessageBox(_("لقد قمت بتغيير بعض الإعدادات التي تتطلب إعادة تشغيل البرنامج لتطبيقها, هل تريد إعادة تشغيل البرنامج الآن؟"), _("تنبيه"), style=wx.YES_NO, parent=self)
			os.execl(sys.executable, sys.executable, *sys.argv) if msg == wx.YES else None
		self.Destroy()

class GeneralSettings(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		wx.StaticText(self, -1, _("لغة البرنامج, يتطلب هذا الأمر إعادة تشغيل البرنامج كَي تتطبق الإعدادات"))
		self.lang=wx.Choice(self, -1)
		self.lang.Set(list(supported_languages.keys()))
		wx.StaticText(self, -1, _("عدد الثواني للتقديم"))
		self.seek=wx.SpinCtrl(self, -1, min=1, max=1800)
		self.seek.Value=get("seek")
		try:
			self.lang.Selection = languages[get("language")]
		except KeyError:
			self.lang.Selection = 0
		self.CFU=wx.CheckBox(self, -1, _("التحقق من وجود تحديثات عند البدئ"))
		self.CFU.SetValue(get("check_for_updates_at_startup"))
		self.LCFU=wx.CheckBox(self, -1, _("التحقق مِن تحديثات اللغة عند البدء"))
		self.LCFU.SetValue(get("languageupdates"))
		self.load_directory_file=wx.CheckBox(self, -1, _("تحميل المسار كاملًا عند فتح ملف, في حال تفعيل هذا الخيار, عند فتح أي ملف, سيقوم البرنامج بفتح الملف مع المجلد كاملًا في البرنامج, هذا يسبب بطء في التحميل"))
		self.load_directory_file.SetValue(get("load_directory_file"))
		self.SaveLast=wx.CheckBox(self, -1, _("حفظ آخر مقطع مع الموضع عند الخروج, يقوم هذا الخيار بالتحقق مِن آخر مقطع تم تشغيله عند البدئ, ثم يقوم بتشغيله والإنتقال إلى النقطة التي تم الوقوف عندها."))
		self.SaveLast.SetValue(get("save_at_exit"))
		self.load_first_file=wx.CheckBox(self, -1, _("تشغيل أول ملف بعد فتح مجلد"))
		self.load_first_file.SetValue(get("load_first_file"))
		self.history=wx.CheckBox(self, -1, _("تفعيل سجل البحث"))
		self.history.SetValue(get("history"))

class SpeakSettings(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		self.speak_pause=wx.CheckBox(self, -1, _("نطق الإيقاف المؤقت والإستئناف"))
		self.speak_pause.SetValue(get("speak_play_pause"))
		self.speak_volume=wx.CheckBox(self, -1, _("نطق مستوى الصوت عند تغييره"))
		self.speak_volume.SetValue(get("speakv"))
		self.speak_fr=wx.CheckBox(self, -1, _("نطق الوقت المنقضي عند التقديم والتأخير"))
		self.speak_fr.SetValue(get("speakfr"))
		self.speakreplayed=wx.CheckBox(self, -1, _("النطق عند إعادة تشغيل المقطع"))
		self.speakreplayed.SetValue(get("speakreplayed"))
		self.speakspeedrate=wx.CheckBox(self, -1, _("نطق معدل السرعة عند تغييره"))
		self.speakspeedrate.SetValue(get("speakspeedrate"))

class HotKeys(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		self.control=wx.CheckBox(self, -1, _("control موصى إستخدامه في windows11 مع الإختصارات الأخرا alt و windows"))
		self.shift=wx.CheckBox(self, -1, "shift")
		self.alt=wx.CheckBox(self, -1, "alt")
		self.win=wx.CheckBox(self, -1, "windows")
		self.replace_pages=wx.CheckBox(self, -1, _("استبدال الأزرار page_up / page_down بالأزرار tab / shift+tab"))
		self.replace_pages.SetValue(get("replace_pages", section="keybord"))
		k=get("hotkeys", "keybord")
		if "control" in k:
			self.control.Value=True
		if "alt" in k:
			self.alt.Value=True
		if "win" in k:
			self.win.Value=True
		if "shift" in k:
			self.shift.Value=True

class subtitles(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		self.read=wx.CheckBox(self, -1, _("قرائة الترجمات"))
		self.AutoDetect=wx.CheckBox(self, -1, _("تحميل ملف الترجمة تلقائيًا"))
		self.sapi=wx.CheckBox(self, -1, _("استخدام sapi5 لِقِراءة الترجمات"))
		wx.StaticText(self, -1, _("اختر الصوت"), name="sapi")
		self.voice=wx.Choice(self, -1, name="sapi")
		test=wx.Button(self, -1, _("اختبار"), name="sapi")
		wx.StaticText(self, -1, _("سرعة القِراءة"), name="sapi")
		self.speed_choice=wx.Choice(self, -1, name="sapi")
		wx.StaticText(self, -1, _("مستوى الصوت"), name="sapi")
		self.volume=wx.Choice(self, -1, name="sapi")
		self.volume.Set([str(i)+"%" for i in range(1, 101)])
		try:
			voices = g.sapi.get_voices()
			voices_list=[i for i in voices]
			self.voice.Set(voices_list)
		except: pass
		try:
			self.voice.Selection = int(get("voice", "subtitles"))
			self.volume.Selection = int(get("volume", "subtitles"))
			self.read.Value = get("read", "subtitles")
			self.AutoDetect.Value=get("autodetect", "subtitles")
			self.sapi.Value=get("sapi", "subtitles")
		except:
			self.voice.Selection = 0
			self.volume.Selection = 4
			self.read.Value = True
			self.AutoDetect.Value = False
			self.sapi.Value = False

		self.OnCheckBox(None)
		self.sapi.Bind(wx.EVT_CHECKBOX, self.OnCheckBox)
		test.Bind(wx.EVT_BUTTON, self.OnTest)
		self.speed_choice.Set([str(i) for i in range(1, 11)])
		self.speed_choice.Selection=int(get("speed", "subtitles"))
		self.Sapi = g.sapi


	def OnCheckBox(self, event):
		if self.sapi.Value==False:
			for i in self.GetChildren():
				i.Hide() if i.Name=="sapi" else None
		else:
			for i in self.GetChildren():
				i.Show() if i.Name=="sapi" else None

	def OnTest(self, event):
		try:
			if self.Sapi.engine.GetStatus() == 2:
				return
			voice = self.voice.Selection
			speed = self.speed_choice.Selection+1
			volume = self.volume.Selection+1
			self.Sapi.set_voice(voice)
			self.Sapi.set_speed(speed)
			self.Sapi.set_volume(volume)
			text="Hello, I am a voice this program using me to read subtitles files, this is an experiment that enables you to know if my voice is clear in reading, thanks for testing me."
			if "leila" in self.voice.StringSelection.lower() or "mehdi" in self.voice.StringSelection.lower() or "nizar" in self.voice.StringSelection.lower() or "salma" in self.voice.StringSelection.lower():
				text="مرحبا, أنا صوت يقوم بإستخدامي هذا البرنامج لِقراءة ملفات الترجمة, هذه تجربة تمكنك من معرفة في حال كان صوتي واضحًا في القراءة, شكرًا على تجربتي."
			Thread(target=self.Sapi.speak, args=[text]).start()
		except: pass

class backup(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		create = wx.Button(self, -1, _("إنشاء نسخة إحتياطية"))
		restore = wx.Button(self, -1, _("إستعادة نسخة إحتياطية"))
		create.Bind(wx.EVT_BUTTON, lambda e:CreateBackup(self))
		restore.Bind(wx.EVT_BUTTON, self.OnRestore)

	def OnRestore(self, event):
		path = wx.FileSelector(_("قم بإختيار نسخة إحتياطية لإستعادتها"), wildcard="|*.zip", parent=self)
		if not path:return
		file = zipfile.ZipFile(path, "r")
		msg = wx.MessageBox(_("إذا قمت بالنقر فوق نعم: ستتم استعادة النسخة الاحتياطية المحددة ، ولا يمكنك التراجع عن هذا الإجراء. هل أنت متأكد أنك تريد استعادة النسخة الاحتياطية؟"), _("تحذير"), style=wx.YES_NO, parent=self)
		if msg==wx.YES:
			file.extractall(spath)
			file.close()
			wx.MessageBox(_("تم استعادة النسخة الاحتياطية بنجاح ، انقر فوق موافق لإعادة تشغيل البرنامج."), _("نجاح"), parent=self)
			return os.execl(sys.executable, sys.executable)


class CreateBackup(wx.Dialog):
	def __init__(self, parent):
		super().__init__(parent, -1, title=_("قم بتحديد الخيارات المرادة, وتحديد المسار في حال كنت تريد تغييره, ثم اضغط فوق موافق للبدأ في أخذ نسخة إحتياطية"))
		p = wx.Panel(self)
		self.otherSettings = wx.CheckBox(p, -1, _("تضمين بيانات المفضلة وبعض البيانات الأخرى مثل قوائم التشغيل"))
		self.otherSettings.Value = True
		self.settings = wx.CheckBox(p, -1, _("تضمين الإعدادات الحالية"))
		self.settings.Value = True
		wx.StaticText(p, -1, _("مسار حفظ النسخة الإحتياطية"))
		self.path = wx.TextCtrl(p, -1)
		self.path.Value = os.path.join(os.getenv("userprofile"), "Documents")
		browse = wx.Button(p, -1, _("تصفح"))
		browse.Bind(wx.EVT_BUTTON, self.OnBrowse)
		start =wx.Button(p, -1, _("موافق"))
		start.Bind(wx.EVT_BUTTON, self.OnStart)
		cancel = wx.Button(p, wx.ID_CANCEL, _("إلغاء"))
		self.Show()

	def OnBrowse(self, event):
		directory = wx.DirDialog(self, _("قم بتحديد مسار الحفظ"), self.path.Value)
		result = directory.ShowModal()
		if result != wx.ID_CANCEL:
			self.path.Value = directory.GetPath()

	def OnStart(self, event):
		os.chdir(spath)
		files = os.listdir()
		if not files: return
		time = datetime.now().strftime(" - %d_%m_%Y %I %p")
		fn = f"media player pro backup {time}.zip"
		file = zipfile.ZipFile(os.path.join(self.path.Value,fn), "w")
		for f in files:
			if os.path.isfile(f):
				file.write(f) if self.settings.Value else None
			else:
				if not self.otherSettings.Value: continue
				files2 = os.listdir(f)
				if not files2: continue
				for f2 in files2:
					file.write(os.path.join(f, f2))
		file.close()
		wx.MessageBox(_("تم أخذ نسخة إحتياطية بنجاح, يمكنك إستعادتها مِن الإعدادات/النسخ الإحتياطي والإستعادة/إستعادة نسخة إحتياطية, مسار النسخة الإحتياطية {path}").format(path=self.path.Value), _("نجاح"), parent=self.Parent)