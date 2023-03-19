import wx
import os
import requests
import threading
import pyperclip
import globals as g
import pafy
from .import youtube
from .history import history
from scripts.web_browser import Open
from .search import YoutubeSearch
from scripts.Speak import speak
from scripts import media_player, subtitle
from datetime import datetime
from settingsconfig import get, new
from time import sleep
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript, NoTranscriptAvailable

countries = {
	'AE': 'United Arab Emirates',
	'AL': 'Albania',
	'AM': 'Armenia',
	'AN': 'Netherlands Antilles',
	'AR': 'Argentina',
	'AT': 'Austria',
	'AU': 'Australia',
	'AZ': 'Azerbaijan',
	'BA': 'Bosnia and Herzegovina',
	'BD': 'Bangladesh',
	'BE': 'Belgium',
	'BF': 'Burkina Faso',
	'BG': 'Bulgaria',
	'BH': 'Bahrain',
	'BI': 'Burundi',
	'BJ': 'Benin',
	'BM': 'Bermuda',
	'BN': 'Brunei Darussalam',
	'BO': 'Bolivia',
	'BR': 'Brazil',
	'BS': 'Bahama',
	'BT': 'Bhutan',
	'BV': 'Bouvet Island',
	'BW': 'Botswana',
	'BY': 'Belarus',
	'BZ': 'Belize',
	'CA': 'Canada',
	'CC': 'Cocos (Keeling) Islands',
	'CF': 'Central African Republic',
	'CG': 'Congo',
	'CH': 'Switzerland',
	'CI': 'Côte D\'ivoire (Ivory Coast)',
	'CK': 'Cook Iislands',
	'CL': 'Chile',
	'CM': 'Cameroon',
	'CN': 'China',
	'CO': 'Colombia',
	'CR': 'Costa Rica',
	'CU': 'Cuba',
	'CV': 'Cape Verde',
	'CX': 'Christmas Island',
	'CY': 'Cyprus',
	'CZ': 'Czech Republic',
	'DE': 'Germany',
	'DJ': 'Djibouti',
	'DK': 'Denmark',
	'DM': 'Dominica',
	'DO': 'Dominican Republic',
	'DZ': 'Algeria',
	'EC': 'Ecuador',
	'EE': 'Estonia',
	'EG': 'Egypt',
	'EH': 'Western Sahara',
	'ER': 'Eritrea',
	'ES': 'Spain',
	'ET': 'Ethiopia',
	'FI': 'Finland',
	'FJ': 'Fiji',
	'FK': 'Falkland Islands (Malvinas)',
	'FM': 'Micronesia',
	'FO': 'Faroe Islands',
	'FR': 'France',
	'FX': 'France, Metropolitan',
	'GA': 'Gabon',
	'GB': 'United Kingdom (Great Britain)',
	'GD': 'Grenada',
	'GE': 'Georgia',
	'GF': 'French Guiana',
	'GH': 'Ghana',
	'GI': 'Gibraltar',
	'GL': 'Greenland',
	'GM': 'Gambia',
	'GN': 'Guinea',
	'GP': 'Guadeloupe',
	'GQ': 'Equatorial Guinea',
	'GR': 'Greece',
	'GS': 'South Georgia and the South Sandwich Islands',
	'GT': 'Guatemala',
	'GU': 'Guam',
	'GW': 'Guinea-Bissau',
	'GY': 'Guyana',
	'HK': 'Hong Kong',
	'HM': 'Heard & McDonald Islands',
	'HN': 'Honduras',
	'HR': 'Croatia',
	'HT': 'Haiti',
	'HU': 'Hungary',
	'ID': 'Indonesia',
	'IE': 'Ireland',
	'IL': 'Israel',
	'IN': 'India',
	'IO': 'British Indian Ocean Territory',
	'IQ': 'Iraq',
	'IR': 'Islamic Republic of Iran',
	'IS': 'Iceland',
	'IT': 'Italy',
	'JM': 'Jamaica',
	'JO': 'Jordan',
	'JP': 'Japan',
	'KE': 'Kenya',
	'KG': 'Kyrgyzstan',
	'KH': 'Cambodia',
	'KI': 'Kiribati',
	'KM': 'Comoros',
	'KN': 'St. Kitts and Nevis',
	'KP': 'Korea, Democratic People\'s Republic of',
	'KR': 'Korea, Republic of',
	'KW': 'Kuwait',
	'KY': 'Cayman Islands',
	'KZ': 'Kazakhstan',
	'LA': 'Lao People\'s Democratic Republic',
	'LB': 'Lebanon',
	'LC': 'Saint Lucia',
	'LI': 'Liechtenstein',
	'LK': 'Sri Lanka',
	'LR': 'Liberia',
	'LS': 'Lesotho',
	'LT': 'Lithuania',
	'LU': 'Luxembourg',
	'LV': 'Latvia',
	'LY': 'Libyan Arab Jamahiriya',
	'MA': 'Morocco',
	'MC': 'Monaco',
	'MD': 'Moldova, Republic of',
	'MG': 'Madagascar',
	'MH': 'Marshall Islands',
	'ML': 'Mali',
	'MN': 'Mongolia',
	'MM': 'Myanmar',
	'MO': 'Macau',
	'MP': 'Northern Mariana Islands',
	'MQ': 'Martinique',
	'MR': 'Mauritania',
	'MS': 'Monserrat',
	'MT': 'Malta',
	'MU': 'Mauritius',
	'MV': 'Maldives',
	'MW': 'Malawi',
	'MX': 'Mexico',
	'MY': 'Malaysia',
	'MZ': 'Mozambique',
	'NA': 'Namibia',
	'NC': 'New Caledonia',
	'NE': 'Niger',
	'NF': 'Norfolk Island',
	'NG': 'Nigeria',
	'NI': 'Nicaragua',
	'NL': 'Netherlands',
	'NO': 'Norway',
	'NP': 'Nepal',
	'NR': 'Nauru',
	'NU': 'Niue',
	'NZ': 'New Zealand',
	'OM': 'Oman',
	'PA': 'Panama',
	'PE': 'Peru',
	'PF': 'French Polynesia',
	'PG': 'Papua New Guinea',
	'PH': 'Philippines',
	'PK': 'Pakistan',
	'PL': 'Poland',
	'PM': 'St. Pierre & Miquelon',
	'PN': 'Pitcairn',
	'PR': 'Puerto Rico',
	'PT': 'Portugal',
	'PW': 'Palau',
	'PY': 'Paraguay',
	'QA': 'Qatar',
	'RE': 'Réunion',
	'RO': 'Romania',
	'RU': 'Russian Federation',
	'RW': 'Rwanda',
	'SA': 'Saudi Arabia',
	'SB': 'Solomon Islands',
	'SC': 'Seychelles',
	'SD': 'Sudan',
	'SE': 'Sweden',
	'SG': 'Singapore',
	'SH': 'St. Helena',
	'SI': 'Slovenia',
	'SJ': 'Svalbard & Jan Mayen Islands',
	'SK': 'Slovakia',
	'SL': 'Sierra Leone',
	'SM': 'San Marino',
	'SN': 'Senegal',
	'SO': 'Somalia',
	'SR': 'Suriname',
	'ST': 'Sao Tome & Principe',
	'SV': 'El Salvador',
	'SY': 'Syrian Arab Republic',
	'SZ': 'Swaziland',
	'TC': 'Turks & Caicos Islands',
	'TD': 'Chad',
	'TF': 'French Southern Territories',
	'TG': 'Togo',
	'TH': 'Thailand',
	'TJ': 'Tajikistan',
	'TK': 'Tokelau',
	'TM': 'Turkmenistan',
	'TN': 'Tunisia',
	'TO': 'Tonga',
	'TP': 'East Timor',
	'TR': 'Turkey',
	'TT': 'Trinidad & Tobago',
	'TV': 'Tuvalu',
	'TW': 'Taiwan, Province of China',
	'TZ': 'Tanzania, United Republic of',
	'UA': 'Ukraine',
	'UG': 'Uganda',
	'UM': 'United States Minor Outlying Islands',
	'US': 'United States of America',
	'UY': 'Uruguay',
	'UZ': 'Uzbekistan',
	'VA': 'Vatican City State (Holy See)',
	'VC': 'St. Vincent & the Grenadines',
	'VE': 'Venezuela',
	'VG': 'British Virgin Islands',
	'VI': 'United States Virgin Islands',
	'VN': 'Viet Nam',
	'VU': 'Vanuatu',
	'WF': 'Wallis & Futuna Islands',
	'WS': 'Samoa',
	'YE': 'Yemen',
	'YT': 'Mayotte',
	'YU': 'Yugoslavia',
	'ZA': 'South Africa',
	'ZM': 'Zambia',
	'ZR': 'Zaire',
	'ZW': 'Zimbabwe',
}
countries = {v:k for k, v in countries.items()}

APIKey = "AIzaSyCEXsh-68oxoE-pdWYEmaa8OwNoMsoFGJI"
pafy.set_api_key(APIKey)
def get_url(url):
	try:
		video=pafy.new(url)
	except ValueError:
		return wx.MessageBox(_("لقد أدخلت رابط غير صالح."), _("خطأ"), style=wx.ICON_ERROR, parent=wx.GetApp().GetTopWindow())
	best=video.getbestaudio()
	burl=best.url
	title=video.title
	info=_("""
		 يتم التشغيل مِن يوتيوب: {title}\n
		المشاهدات: {views}\n
		المالك: {author}\n
		عدد الإعجابات: {likes}\n
		الوصف: {description}
	""").format(title=video.title, author=video.author, views=video.viewcount, likes=video.likes, description=video.description)
	g.youtube_description = video.description
	return [burl, info, title, url]

class SearchDialog(wx.Dialog):
	def __init__(self, parent, search_word=None, from_history=False):
		wx.Dialog.__init__(self, parent, title=_("البحث في يوتيوب"))
		self.from_history=from_history
		self.p=wx.Panel(self)
		self.CenterOnParent()
		self.setup_context()
		wx.StaticText(self.p, -1, _("كلمة البحث"))
		self.query=wx.TextCtrl(self.p, -1, style=wx.TE_PROCESS_ENTER)
		wx.StaticText(self.p, -1, _("قائمة النتائج"), name="result")
		self.Results=wx.ListBox(self.p, -1, name="result")
		self.Results.Bind(wx.EVT_CHAR_HOOK, self.OnMenu)
		self.Results.Bind(wx.EVT_LISTBOX, self.listbox)
		self.LoadAll=wx.CheckBox(self.p, -1, _("تحميل جميع النتائج الحالية في قائمة"), name="result")
		close=wx.Button(self.p, -1, _("إغلاق"))
		close.Bind(wx.EVT_BUTTON, lambda e:self.Hide())
		self.Bind(wx.EVT_TEXT_ENTER, self.startsearch)
		self.Bind(wx.EVT_CHAR_HOOK, self.shortcuts)
		self.search=None
		if not search_word is None:
			g.search_window=self
			self.query.Value=search_word
			self.query.SetFocus()
			self.Show()
			self.startsearch(None)


	def startsearch(self, event):
		if self.query.Value=="": return
		self.Results.SetFocus()
		threading.Thread(target=self.searchyt, args=[self.query.Value]).start()

	def searchyt(self, query):
		speak(_("يتم البحث عن {q}").format(q=query))
		try:
			self.search=YoutubeSearch(query)
		except:
			wx.MessageBox(_("حدث خطأ أثناء محاولة البحث, قد تكون هناك مشكلة بالإتصال, إذا استمرت المشكلة بالظهور قم بمراسلة المطور لحل المشكلة"), _("خطأ"), parent=self, style=wx.ICON_ERROR)
			return
		titles = self.search.get_titles()
		speak(_("اكتمل تحميل النتائج"))
		self.Results.Set(titles)
		for i in self.p.GetChildren():
			i.Show() if i.Name=="result" and i.Shown==False else None
		try:
			self.Results.SetSelection(0)
		except: pass
		if get("history") and not self.from_history:
			date=datetime.now().strftime("%d/%m/%Y")
			h=history().add_to_date(date, self.query.Value)
		if self.from_history:
			try:
				sleep(0.5)
				self.from_history.Destroy()
			except:
				pass
		self.query.Value=""


	def OnMenu(self, event):
		key=event.GetKeyCode()
		if key==wx.WXK_RETURN:
			if len(self.Results.Strings)<1: return
			index=self.Results.Selection
			g.youtube_url=self.search.get_url(index)
			data=youtube.get_url(g.youtube_url)
			try:
				link=data[0]
			except:
				return
			g.youtube_file_info=data[1]
			title=data[2]
			g.tracks_list=[]
			g.playing_from_youtube=True
			if self.LoadAll.Value==True:
				for track in range(len(self.Results.Strings)):
					g.tracks_list.append([self.search.get_title(track), self.search.get_url(track)])
				g.index = index
			if g.player==None:
				g.player=media_player.Player(link, wx.GetApp().GetTopWindow().GetHandle())
				g.set_title(title)
				g.player.title=title
				g.player.url=g.youtube_url
				self.Hide()
				wx.GetApp().GetTopWindow().SetFocus()
				return
			try:
				g.player.media.stop()
			except: pass
			g.player.set_media(link)
			g.playing_from_youtube=True
			g.set_title(title)
			g.player.title=title
			g.player.url=g.youtube_url
#			g.tracks_list=[]
			g.folder_path=""
			g.player.media.play()
			self.Hide()
			wx.GetApp().GetTopWindow().SetFocus()
		event.Skip()

	def listbox(self, event):
		if self.Results.Strings==[]:
			return
		if self.Results.Selection==len(self.Results.Strings)-1:
			speak(_("يتم تحميل المزيد من النتائج"))
			if self.search.load_more() is None:
				return speak(_("لا توجد نتائج أُخرى"))
			threading.Thread(target=self.load_more).start()
			speak(_("تم تحميل المزيد من النتائج"))

	def load_more(self):
		self.Results.Append(self.search.get_last_titles())

	def shortcuts(self, event):
		key=event.GetKeyCode()
		if key==wx.WXK_ESCAPE:
			self.Hide()
			wx.GetApp().GetTopWindow().SetFocus()
		event.Skip()

	def setup_context(self):
		self.context=wx.Menu()
		open_in_browser=self.context.Append(-1, _("فتح الفيديو في المتصفح\tv"))
		open_channel_in_browser=self.context.Append(-1, _("فتح القناة في المتصفح\tc"))
		copy_video_link=self.context.Append(-1, _("نسخ رابط الفيديو\tu"))
		copy_channel_link=self.context.Append(-1, _("نسخ رابط القناة\tl"))
		self.Bind(wx.EVT_MENU, self.OpenVideoInBrowser, open_in_browser)
		self.Bind(wx.EVT_MENU, self.OpenChannelInBrowser, open_channel_in_browser)
		self.Bind(wx.EVT_MENU, lambda e: pyperclip.copy(self.search.get_url(self.Results.Selection)), copy_video_link)
		self.Bind(wx.EVT_MENU, lambda e: pyperclip.copy(self.search.get_channel(self.Results.Selection)["url"]), copy_channel_link)
		def popup():
			if len(self.Results.Strings)>1 and self.FindFocus()==self.Results and not self.Results.Selection==-1:
				self.PopupMenu(self.context)
		self.Bind(wx.EVT_CONTEXT_MENU, lambda e:popup())

	def OpenVideoInBrowser(self, event):
		speak(_("يتم الفتح في المتصفح"))
		Open(self.search.get_url(self.Results.Selection))

	def OpenChannelInBrowser(self, event):
		speak(_("يتم الفتح في المتصفح"))
		Open(self.search.get_channel(self.Results.Selection)["url"])

class SelectCountry(wx.Dialog): #small class for select a country
	def __init__(self, parent):
		super().__init__(parent, -1, _("تحديد البلد"))
		p = wx.Panel(self)
		wx.StaticText(p, -1, _("البلد"))
		self.country = wx.Choice(p, -1)
		ok = wx.Button(p, -1, _("موافق"))
		ok.Bind(wx.EVT_BUTTON, self.OnOk)
		ok.SetDefault()
		cancel = wx.Button(p, wx.ID_CANCEL, _("إلغاء"))
		for con in countries:
			self.country.Append(con)
		self.country.Selection = 0
		self.ShowModal()

	def OnOk(self, event):
		c = countries[self.country.StringSelection]
		new("country", c)
		speak(_("تم تعيين البلد على {C}").format(C=self.country.StringSelection))
		self.Destroy()

class trend(wx.Dialog):
	def __init__(self, parent):
		super().__init__(parent, -1, title=_("فيديوهات رائجة على يوتيوب"))
		Country = None
		try:
			Country = get("country")
		except: pass
		if Country == None or Country == "none":
			SelectCountry(self)
		if Country == None or Country == "none":
			self.Destroy()
		p = wx.Panel(self)
		self.trends = []
		self.nextPageToken = None
		self.index = 0
		self.trendList = wx.ListBox(p, -1)
		self.trendList.Bind(wx.EVT_LISTBOX, self.OnEnd)
		self.trendList.Bind(wx.EVT_CHAR_HOOK, self.OnChoice)
		self.loadAll = wx.CheckBox(p, -1, _("تحميل جميع النتائج الحالية في قائمة"))
		self.setCountry = wx.Button(p, -1, _("{ccode} إعادة تعيين البلد").format(ccode=get("country")))
		self.setCountry.Bind(wx.EVT_BUTTON, self.ReSetCountry)
		close = wx.Button(p, wx.ID_CANCEL, _("إغلاق"))
		self.initialize()
		self.Show()

	def ReSetCountry(self, event):
		SelectCountry(self)
		self.trends = []
		self.trendList.Clear()
		self.initialize()
		self.setCountry.SetLabel(_("{ccode} إعادة تعيين البلد").format(ccode=get("country")))
		self.trendList.SetFocus()

	def initialize(self, token=None):
		base_url = "https://www.youtube.com/watch?v="
		api_endpoint = "https://www.googleapis.com/youtube/v3/videos"
		params = {
			"part": "snippet,statistics",
			"chart": "mostPopular",
			"regionCode": get("country"),
			"maxResults": 20,
			"key": APIKey,
		}
		if token is not None:
			params["pageToken"] = token
		response = requests.get(api_endpoint, params=params)
		data = response.json()
		if "nextPageToken" in data:
			self.nextPageToken = data["nextPageToken"]
		else:
			self.nextPageToken = None
		try:
			videos = data['items']
		except KeyError:
			wx.MessageBox(_("عذرًا, لا تتوفر فيديوهات رائجة لِهذا البلد"), _("خطأ"), parent=self.Parent, style=wx.ICON_ERROR)
			new("country", "none")
		for vid in videos:
			id = vid["id"]
			url = base_url + id
			r = {
				"title":vid["snippet"]["title"],
				"views":vid["statistics"]["viewCount"],
				"likes":vid["statistics"]["likeCount"],
				"channel":vid["snippet"]["channelTitle"],
				"published":vid["snippet"]["publishedAt"],
				"url":url
			}
			self.trends.append(r)
		if self.trendList.Selection==-1:
			i = 0
		else:
			i = self.trendList.Selection
		for trend in self.trends[i:]:
			timestamp = trend["published"]
			datetime_obj = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
			time = datetime_obj.strftime("%d/%m/%Y")
			self.trendList.Append(_("{title}, بواسطة: {by}, المشاهدات: {views}, عدد الإعجابات: {likes}, تاريخ النشر: {published}").format(title=trend["title"], by=trend["channel"], views=trend["views"], likes=trend["likes"], published=time))
		self.trendList.Selection = i

	def OnEnd(self, event):
		if self.trendList.GetSelection() == self.trendList.GetCount() - 1:
			if self.nextPageToken == None: return speak(_("لا يوجد المزيد مِن الفيديوهات الرائجة"))
			self.initialize(self.nextPageToken)

	def OnChoice(self, event):
		key=event.GetKeyCode()
		if key==wx.WXK_RETURN:
			if len(self.trendList.Strings)<1: return
			index=self.trendList.Selection
			g.youtube_url=self.trends[index]["url"]
			data=youtube.get_url(g.youtube_url)
			try:
				link=data[0]
			except:
				return
			g.youtube_file_info=data[1]
			title=data[2]
			g.tracks_list=[]
			g.playing_from_youtube=True
			if self.loadAll.Value:
				for track in range(len(self.trendList.Strings)):
					g.tracks_list.append([self.trends[track]["title"], self.trends[track]["url"]])
				g.index = index
			if g.player==None:
				g.player=media_player.Player(link, wx.GetApp().GetTopWindow().GetHandle())
				g.set_title(title)
				g.player.title=title
				g.player.url=g.youtube_url
				self.Hide()
				wx.GetApp().GetTopWindow().SetFocus()
				return
			try:
				g.player.media.stop()
			except: pass
			g.player.set_media(link)
			g.playing_from_youtube=True
			g.set_title(title)
			g.player.title=title
			g.player.url=g.youtube_url
#			g.tracks_list=[]
			g.folder_path=""
			g.player.media.play()
			self.Hide()
			wx.GetApp().GetTopWindow().SetFocus()
		event.Skip()

class translations(wx.Dialog):
	def __init__(self, parent):
		if not g.playing_from_youtube: return speak(_("لم يتم التشغيل من يوتيوب"))
		self.lst = []
		super().__init__(parent, -1, _("ترجمات الفيديو"))
		p = wx.Panel(self)
		wx.StaticText(p, -1, _("اختر ترجمة"))
		self.translist = wx.ListBox(p, -1)
		self.translist.Bind(wx.EVT_CHAR_HOOK, self.OnList)
		close = wx.Button(p, wx.ID_CANCEL, _("إغلاق"))
		self.GetTranslations()
		self.translist.Selection = 0
		self.Show()

	def GetTranslations(self):
		videoId = g.youtube_url.split("https://www.youtube.com/watch?v=")[1]

		try:
			self.lst = YouTubeTranscriptApi.list_transcripts(videoId)
		except TranscriptsDisabled:
			return speak(_("لا توجد ترجمات لهذا الفيديو"))
		for transcript in self.lst:
			self.translist.Append(f"{transcript.language_code}, {transcript.language}")

	def OnList(self, event):
		if event.GetKeyCode()==wx.WXK_RETURN:
			selection = self.translist.StringSelection.split(",")[0]
			for script in self.lst:
				if script.language_code == selection:
					t = script.fetch()
					srt = SRTFormatter().format_transcript(t)
					temp_path = os.path.join(os.environ['TEMP'], 'srt.srt')
					with open(temp_path, "w", encoding="utf-8") as f:
						f.write(srt)
					subtitle.load(temp_path, temp=True)
					speak(_("تم تحميل الترجمة {translation} بنجاح").format(translation=self.translist.StringSelection.split(",")[1]))
					self.Destroy()
		event.Skip()