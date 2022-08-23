import pysubs2
from .Speak import speak
import datetime as dt
import globals as g
import wx
import os

def load(path):
	try:
		data=pysubs2.load(path, encoding="utf-8")
	except:
		data=pysubs2.load(path, encoding="ansi")
	for i in data:
		g.current_subtitle[g.time_to_ms(dt.datetime.utcfromtimestamp(i.start//1000).strftime("%H:%M:%S"))] = {"text":i.text.replace(r"\N", "\n"), "start":dt.datetime.utcfromtimestamp(i.start//1000).strftime("%H:%M:%S"), "end":dt.datetime.utcfromtimestamp(i.end//1000).strftime("%H:%M:%S")}

def Select():
		path=wx.FileSelector(_("اختيار ملف ترجمة (.srt)|*.srt"))
		if not path: return
		load(path)

def auto_detect(path):
	try:
		types=["srt"]
		directory = os.path.dirname(path)
		FileName = os.path.splitext(os.path.basename(path))[0]
		path = f"{directory}/{FileName}"
		for t in types:
			if os.path.exists(f"{path}.{t}"):
				load(f"{path}.{t}")
				speak(_("تم تحميل ملف الترجمة {subfile}").format(subfile=os.path.basename(path+"."+t)))
				break
	except Exception as e:
		print(e)