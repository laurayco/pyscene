import pygame
from promise import MetaEvent, Promise
from functools import partial

def consume(x):
	for y in x:pass

def isinstancereverse(t,o):return isinstance(o,t)

class NodeObject:
	def __init__(self,node):
		self.node=node
		self.get_child = self.node.sub_nodes.get
	def get_children(self,objects=True,filters=None):
		filters = filters or []
		def get_all():
			for name,node in self.node.sub_nodes.items():
				if all([f(node) for f in filters]):
					val = node.runtime_object if objects and node.runtime_object else node
					yield name,val
		return dict(get_all())
	def require_child(self,satisfies):
		for name,node in self.get_children(False).items():
			if satisfies(name,node):
				yield name,node
	def tick(self,manager,*a,**k):pass

class Timer(NodeObject):
	def __init__(self,node,frequency,buffer=False):
		super().__init__(node)
		self.timer = pygame.time.Clock()
		self.elapsed = 0
		self.buffer = buffer
		self.on_elapse = MetaEvent()
		self.frequency = frequency
	def tick(self):
		self.elapsed += self.timer.tick()
		if self.buffer:
			self.on_elapse(round(self.elapsed/self.frequency))
			self.elapsed = 0
		else:
			while self.elapsed > self.frequency:
				self.elapsed -= self.frequency
				self.on_elapse(1)

class Animation(NodeObject):
	def __init__(self,node,repeat=None,direction=1):
		super().__init__(node)
		# assert that there is at least one animation channel involved.
		assert len(tuple(self.require_child(partial(isinstancereverse,AnimationChannel))))>0
		self.repeat = repeat
		self.direction = direction
		#to-do: calculate max number of steps needed.
		#       [ use sub_nodes to determine this. ]
	def calculate(self,remaining):
		channels = {}
		for path,node in self.get_children(True,filters=[lambda name,node:isinstance(node.runtime_object,AnimationChannel)]):
			channels[path]=node.calculate(self.completion)
		self.on_calculate(channels)

class AnimationChannel(NodeObject):
	def __init__(self,node,start=0,final=100,method='linear'):
		super().__init__(node)
		self.start = start
		self.final = final
		self.method = method
	def get_value(self,percentage):
		difference,direction=abs(self.final-self.end),-1 if self.start>self.end else 1
		if self.method=='linear':
			return percentage * direction * difference
		elif self.method=='squared':
			return percentage**2 * direction * difference

class Window(NodeObject):
	def __init__(self,node,press_threshold=250):
		super().__init__(node)
		self.press_threshold = press_threshold
		self.on_click = MetaEvent()
		self.on_keydown = MetaEvent()
		self.on_keyup = MetaEvent()
		self.on_keypress = MetaEvent()#triggered if more than press_threshold ms pass before keyup event.
	def tick(self,manager,*a,**k):
		consume(map(self.handle_event,pygame.event.get()))

class Camera(NodeObject):
	def __init__(self,node):
		super().__init__(node)
	def get_painted_objects(self):
		"""Return an iterable object of all
		objects that should be painted on by
		this thing"""
		return iter([])
	def get_old_objects(self):
		gpo = self.get_painted_objects()
		return filter(lambda o:o.is_visible() and o.needs_repaint() for o in gpo)
	def needs_to_draw(self):return len(self.get_old_objects())>0
	def draw_objects(self,surf):
		for painted_obj in self.get_old_objects():
			painted_obj.paint(surf)

class PaintedObject(NodeObject):
	def __init__(self,node):
		super().__init__(node)
	def needs_repaint(self):
		"""Return True if when calling 'paint',
		there should be a different output than
		the last draw."""
		return False
	def is_visible(self,camera):
		"""Return True if the object should
		be visible on the screen. eg: return
		false when the object is off-screen."""
		return False
	def paint(self,surface):
		"""Update surface according to your object."""
		pass

class ColorFade(Animation):
	def __init__(self,node,direction='alternate',repeat=0):
		super().__init__(node,repeat,direction)
		ischannel = partial(isinstancereverse,AnimationChannel)
		assert self.get_child('red') is not None
		assert self.get_child('green') is not None
		assert self.get_child('blue') is not None

class ColorPulser(PaintedObject):
	def __init__(self,node):
		super().__init__(node)
		self.color_animation = self.get_child('color')
		assert self.color_animation is not None
		self.color = self.color_animation.calculate()
	def on_animation_update(self,animation):
		r = animation.red_channel
	def needs_repaint(self): return True
	def is_visible(self): return True
	def paint(self,surface): surface.fill(self.color)

class Screen(NodeObject):
	def __init__(self,node,resolution=(320,240),flags=0):
		super().__init__(node)
		self.resolution = resolution
		self.window_flags = flags
	def ensure_window(self):
		if not pygame.display.get_init():
			pygame.display.init()
		if not pygame.display.get_surface():
			pygame.display.set_mode(self.resolution,self.window_flags)
	def tick(self,manager,*a,**k):
		needs_update = []
		def is_camera(node):
			return isinstance(node.runtime_object,PaintedObject)
		for name,camera in self.get_children(objects=True,filters=[is_camera]):
			if camera.needs_to_draw():
				needs_update.append(camera)
		if len(needs_update)>0:
			self.ensure_window()
			window = pygame.display.get_surface()
			for camera in needs_update:
				camera.draw_objects(window)
