#!/usr/bin/env python

import json, imp, os, functools
from promise import MetaEvent, Promise

split_pieces = lambda s,n:iter(t.strip() for t in s.split(n))

class ModuleCache:
	@classmethod
	@functools.lru_cache(10)
	def get_module(cls,name):
		return imp.load_source(name[-1],os.path.sep.join(name)+".py")
	@classmethod
	def load_object(cls,*scope):
		module,typename=scope[:-1],scope[-1]
		return getattr(cls.get_module(module),typename)

class SceneNode:
	def __init__(self,name,graphnode,parent=None):
		self.name = name
		self.parent = parent
		subs = graphnode.get('sub_nodes',{})
		self.sub_nodes = dict((name,SceneNode(name,node,self)) for name,node in subs.items())
		runtime_type = graphnode['type']
		if runtime_type:
			args, kwargs = graphnode.get('args',[]),graphnode.get('kwargs',{})
			self.runtime_object = SceneNode.make_object(self,runtime_type,*args,**kwargs)
	@classmethod
	def make_object(cls,node,typename,*args,**kwargs):
		rt_type = ModuleCache.load_object(*list(split_pieces(typename,".")))
		return rt_type(node,*args,**kwargs)
	def tick(self,scene_manager,*a,**k):
		self.runtime_object.tick(scene_manager,*a,**k)

class SceneScope:
	def __init__(self,root_scene,scope=None):
		self.root_scene = root_scene
		self.scope_frequency = scope or {}
		self.tick_step = 0
	def tick(self,manager,*a,**k):
		self.tick_step += 1
		for path,ticks in self.scope_frequency.items():
			if ticks==1 or self.tick_step%ticks==0:#ran every tick
				self.get_node(path).tick(manager,*a,**k)
	def get_node(self,path,root_node=None):
		root_node = root_node or self.root_scene
		path = list(split_pieces(path,".")) if isinstance(path,str) else path
		if len(path)>1:
			return self.get_node(path[1:],root_node.sub_nodes[path[0]])
		return root_node.sub_nodes[path[0]]

class SceneManager:
	available = True
	def __init__(self,initial_scene,initial_scope):
		self.initial_scene = self.scene = initial_scene
		self.initial_scope = self.scope = initial_scope
	def tick(self,*a,**k):
		self.scope.tick(self,*a,**k)

if __name__=="__main__":
	from sys import argv; argv=argv[1:]
	scene,scope=None,None
	try:
		assert len(argv)==2
		with open(argv[0]) as f:
			scene = SceneNode(argv[0],json.load(f))
			with open(argv[1]) as ff:
				scope = SceneScope(scene,json.load(ff))
	except AssertionError:
		print("Usage: scene.py <scene_file> <scope_file>")
	finally:
		if scene and scope:
			mgr = SceneManager(scene,scope)
			while mgr.available: mgr.tick()