import json

split_species = lambda s,n:"".join(t.strip() for t in s.split(n))

class MetaEvent:
	def __init__(self):self.handlers=[]
	def __call__(self,*a,**k):
		for e in self.handlers:
			e(*a,**k)

class Promise:
	def __init__(self):
		self.on_resolve = MetaEvent()
		self.on_reject = MetaEvent()
		self.then = self.on_resolve.handlers.append
		self.catch = self.on_reject.handlers.append

class Deferred:
	def __init__(self):self.promises = []
	def push(self,o):self.promises.append(o)
	def pop(self):
		r,self.promises=self.promises[-1],self.promises[:-1]
		return r
	def resolve(self,*a,**k):self.pop().on_resolve(*a,**k)
	def reject(self,*a,**k):self.pop().on_reject(*a,**k)
	def promise(self):self.push(Promise())

class SceneNode:
	def __init__(self,name,graphnode):
		self.name = name
		self.sub_nodes = dict(name,SceneNode(name,node) for name,node in graphnode['sub_nodes'])
		runtime_type = graphnode['type']
		runtime_args, runtime_kwargs = graphnode['args'],graphnode['kwargs']
		self.runtime_object = SceneNode.make_object(runtime_type,*runtime_args,**runtime_kwargs)
	@classmethod
	def make_object(cls,typename,*args,**kwargs):
		typename = split_pieces(typename,".")
		module,instance = typename[:-1],typename[-1]
		#instance = load_module(module)[instance]
		#instance = instance(*args,**kwargs)
		return instance

class SceneScope:
	def __init__(self,root_scene):
		root_scene = root_scene if isinstance(root_scene,SceneNode) else SceneNode(root_scene)
		self.root_scene = root_scene
		self.scope_frequency = {}
		self.tick_step = 0

class SceneManager:
	def __init__(self,initial_scene,initial_scope):
		self.initial_scene = self.scene = initial_scene
		self.initial_scope = self.scope = initial_scope
	def load_scope(