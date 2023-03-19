import application
import wx
from settingsconfig import get
import re

programPath = ""

tracks_list=[] #a list to save the links if from youtube, or paths from folder.
FavoriteLength={} #a dictionary to save the lengths (elapsed) of loaded favorite category
FavoriteLoaded = False # a bool variable to check if folder loaded or a favorite category to use the next / previous currectly
folder_path="" # the path of loaded folder
filePath = "" # store current playing file path
index=0 # the tracks list current index
player=None # the media player object
m3u = False
mindex = 0
handle=None # the window handler
parent=None # the main window parent
pathloop=True # a bool variable to run the open with loop
random_play=False # to play from tracks list randomly
current_subtitle={}
hy=None
playing_from_youtube=False # a bool variable to check if playing from youtube or not
youtube_url="" # the current playing media url, using to get comments etc.
youtube_file_info = ""
youtube_description = ""
youtube_list=[]
sapi = None # sapi object to give more control
fromUrl = False

def time_formatting( t):
	t = t.split(":")
	t = [int(i) for i in t]
	t.pop(0) if t[0] == 0 else None
	def minute(m):
		if m == 1:
			return _("دقيقة واحدة")
		elif m == 2:
			return _("دقيقتان")
		elif m >=3 and m <=10:
			return _("{} دقائق").format(m)
		else:
			return _("{} دقيقة").format(m)
	def second(s):
		if s == 1:
			return _("ثانية")
		elif s == 2:
			return _("ثانيتين")
		elif s >= 3 and s <= 10:
			return _("{} ثواني").format(s)
		else:
			return _("{} ثانية").format(s)
	def hour(h):
		if h == 1:
			return _("ساعة")
		elif h == 2:
			return _("ساعتان")
		elif h >= 3 and h <=10:
			return _("{} ساعات").format(h)
		else:
			return _("{} ساعة").format(h)
	if len(t) == 1:
		return second(t[0])
	elif len(t) == 2:
		return _("{} و{}").format(minute(t[0]), second(t[1]))
	elif len(t) == 3:
		return _("{} و{} و{}").format(hour(t[0]), minute(t[1]), second(t[2]))

def set_title(title):
	wx.GetApp().GetTopWindow().Title=f"{title} {application.name}"

def time_to_ms(timestamp):
	timestamp = timestamp.split(":")
	timestamp  =[int(t)  for t in timestamp]
	ms = 0
	for i in range(1, len(timestamp)+1):
			ms += timestamp[-i] * 1000*60**(i-1)
	return ms

def IsYoutubeUrl(string):
	pattern = re.compile("^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$") # youtube links regular expression pattern
	return pattern.search(string)
