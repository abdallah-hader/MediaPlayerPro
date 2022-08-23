import gettext
from settingsconfig import get
from collections import OrderedDict

supported_languages = OrderedDict({
	"العربية": "ar",
	"English": "en",
	"spanish":"es",
	"turkish":"tr",
	"French":"fr",
})

def init_translation(domaine):
	try:
		translation=gettext.translation(domaine, localedir='languages', languages=[get("language")])
	except:
		translation=gettext.translation(domaine, fallback=True)
	translation.install()
