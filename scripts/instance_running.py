import os
import psutil

def check(process_name, id):
	for process in psutil.process_iter():
		if process_name.lower() in process.name().lower() and process.pid!=id:
			return True
	return False