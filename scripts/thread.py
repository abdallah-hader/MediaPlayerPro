import threading
import ctypes



class Thread(threading.Thread):
 def __init__(self, target, *args, **kwargs):
  super().__init__()
  self.target = target
  self.args = args
  self.kwargs = kwargs 
  self.demon=True
 def run(self):
  try:
   self.target(*self.args, **self.kwargs)
  finally:
   pass
 def get_id(self):
  if hasattr(self, '_thread_id'):
   return self._thread_id
  for id, thread in threading._active.items():
   if thread is self:
    return id
 def stop(self):
  ctypes.pythonapi.PyThreadState_SetAsyncExc(self.get_id(), ctypes.py_object(SystemExit))