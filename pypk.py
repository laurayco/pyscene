#!/usr/bin/env python

import json

split_pieces = lambda s,n:iter(t.strip() for t in s.split(n))

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
		subs = graphnode.get('sub_nodes',{})
		self.sub_nodes = dict((name,SceneNode(name,node)) for name,node in subs.items())
		runtime_type = graphnode['type']
		runtime_args, runtime_kwargs = graphnode.get('args',[]),graphnode.get('kwargs',{})
		self.runtime_object = SceneNode.make_object(runtime_type,*runtime_args,**runtime_kwargs)
	@classmethod
	def make_object(cls,typename,*args,**kwargs):
		typename = list(split_pieces(typename,"."))
		module,instance = typename[:-1],typename[-1]
		#instance = load_module(module)[instance]
		#instance = instance(*args,**kwargs)
		return instance
	def tick(self,scene_manager,scene_scope,*a,**k):
		print(self.runtime_object,self.name)

class SceneScope:
	def __init__(self,root_scene,scope=None):
		self.root_scene = root_scene
		self.scope_frequency = scope or {}
		self.tick_step = 0
	def tick(self,manager,*a,**k):
		self.tick_step += 1
		for path,ticks in self.scope_frequency.items():
			if ticks==1 or self.tick_step%ticks==0:#ran every tick
				self.get_node(path).tick(manager,self,*a,**k)
	def get_node(self,path,root_node=None):
		root_node = root_node or self.root_scene
		path = list(split_pieces(path,".")) if isinstance(path,str) else path
		if len(path)>1:
			return self.get_node(path[1:],root_node.sub_nodes[path[0]])
		return root_node.sub_nodes[path[0]]

class SceneManager:
	def __init__(self,initial_scene,initial_scope):
		self.initial_scene = self.scene = initial_scene
		self.initial_scope = self.scope = initial_scope
	def tick(self,*a,**k):
		self.scope.tick(self,*a,**k)

if __name__=="__main__":
	root_node = SceneNode("title_screen",{
		"type":"pypk.TitleScreen",
		"sub_nodes":{
			"text_flasher":{
				"type":"pypk.TextFlasher",
				"args":["Press `Enter` to continue!"],
				"sub_nodes":{
					"exit_titlescreen":{
						"type":"pypk.ContinueOnEnter",
					}
				}
			}
		}
	})
	root_scope = SceneScope(root_node,{
		"text_flasher":4,
		"text_flasher.exit_titlescreen":1
	})
	manager = SceneManager(root_node,root_scope)
	while True:
		manager.tick()