import wx
import os
from settingsconfig import get, new
import sys
from language import supported_languages
from scripts.Speak import speak
from scripts.Speak import sapi
from threading import Thread

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
		if not float(get("volume", "subtitles")) == self.subtitles.volume.Value:
			new("volume", self.subtitles.volume.Value, "subtitles")
			restart=True
		if not int(get("voice", "subtitles")) == self.subtitles.voice.Selection:
			new("voice", self.subtitles.voice.Selection, "subtitles")
			restart=True
		if not int(get("speed", "subtitles")) == self.subtitles.speed_choice.Selection:
			new("speed", self.subtitles.speed_choice.Selection, "subtitles")
			restart=True
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
		self.seek=wx.SpinCtrl(self, -1, min=1, max=60)
		self.seek.Value=get("seek")
		try:
			self.lang.Selection = languages[get("language")]
		except KeyError:
			self.lang.Selection = 0
		self.CFU=wx.CheckBox(self, -1, _("التحقق من وجود تحديثات عند البدئ"))
		self.CFU.SetValue(get("check_for_updates_at_startup"))
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
		self.speed_rate={"بطيء جدا":10, "بطيء":70, "متوسط":180, "سريع":220, "سريع جدا":300}
		self.speeds=[_("بطيء جدا"), _("بطيء"), _("متوسط"), _("سريع"), _("سريع جدا")]
		self.read=wx.CheckBox(self, -1, _("قرائة الترجمات"))
		self.read.Value=get("read", "subtitles")
		self.AutoDetect=wx.CheckBox(self, -1, _("تحميل ملف الترجمة تلقائيًا"))
		self.AutoDetect.Value=get("autodetect", "subtitles")
		self.sapi=wx.CheckBox(self, -1, _("استخدام sapi5 لِقِراءة الترجمات"))
		wx.StaticText(self, -1, _("اختر الصوت"), name="sapi")
		self.voice=wx.Choice(self, -1, name="sapi")
		test=wx.Button(self, -1, _("اختبار"), name="sapi")
		wx.StaticText(self, -1, _("سرعة القِراءة"), name="sapi")
		self.speed_choice=wx.Choice(self, -1, name="sapi")
		wx.StaticText(self, -1, _("مستوى الصوت"), name="sapi")
		self.volume=wx.SpinCtrlDouble(self, -1, min=0.1, max=1.0, inc=0.1, name="sapi")
		self.volume.Value=get("volume", "subtitles")
		sapi5=sapi()
		voices=sapi5.get_voices()
		voices_list=[i for i in voices]
		self.voice.Set(voices_list)
		try:
			self.voice.SetStringSelection(voices_list[int(get("voice", "subtitles"))])
		except:
			self.voice.Selection=0
		self.sapi.Value=get("sapi", "subtitles")
		self.OnCheckBox(None)
		self.sapi.Bind(wx.EVT_CHECKBOX, self.OnCheckBox)
		test.Bind(wx.EVT_BUTTON, self.OnTest)
		self.speed_choice.Set(self.speeds)
		self.speed_choice.Selection=int(get("speed", "subtitles"))

	def OnCheckBox(self, event):
		if self.sapi.Value==False:
			for i in self.GetChildren():
				i.Hide() if i.Name=="sapi" else None
		else:
			for i in self.GetChildren():
				i.Show() if i.Name=="sapi" else None

	def OnTest(self, event):
		s=sapi()
		voice=self.voice.GetStringSelection()
		speed=self.speed_rate[self.speed_choice.GetStringSelection()]
		volume=self.volume.Value
		s.set_voice(s.get_voice_id(voice))
		s.set_speed(speed)
		s.set_volume(volume)
		text="Hello, I am a voice this program using me to read subtitles files, this is an experiment that enables you to know if my voice is clear in reading, thanks for testing me."
		if "leila" in voice.lower() or "mehdi" in voice.lower() or "nizar" in voice.lower() or "salma" in voice.lower():
			text="مرحبا, أنا صوت يقوم بإستخدامي هذا البرنامج لِقراءة ملفات الترجمة, هذه تجربة تمكنك من معرفة في حال كان صوتي واضحًا في القراءة, شكرًا على تجربتي."
		Thread(target=s.speak, args=[text]).start()