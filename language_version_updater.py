import os
import glob

os.chdir(os.path.dirname(__file__))

all = glob.glob("languages/*/lc_messages/version.txt")

for ver in all:
	current = open(ver, "r").read()
	version = input("the {n} version is {v} if you want to update type the new version and press enter else press enter with out type anything".format(n=ver.split("\\")[1], v=current))
	if version:
		with open(ver, "w", encoding="utf-8") as f:
			f.write(version)