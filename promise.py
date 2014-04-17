class MetaEvent:
	def __init__(self):
		self.handlers=[]
		self.__call__ = lambda:[e(*a,**k)for e in self.handlers]

class Promise:
	def __init__(self):
		self.on_resolve = MetaEvent()
		self.on_reject = MetaEvent()
		self.then = self.on_resolve.handlers.append
		self.catch = self.on_reject.handlers.append