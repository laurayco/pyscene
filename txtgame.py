
class TextFlasher:
	def __init__(self,text):
		self.text, blink_a, blink_b = text, "", ""
		for i in range(len(text)):
			if i%2:blink_a, blink_b = blink_a + ' ', blink_b + text[i]
			else:  blink_b, blink_a = blink_b + ' ', blink_a + text[i]
		self.step = 0
		self.blink_a,self.blink_b=blink_a,blink_b
	def tick(self,node,scene_manager):
		self.step = [1,2,0][self.step]
		if self.step<1:
			self.output(self.text)
		elif self.step<2:
			self.output(self.blink_a)
		else:
			self.output(self.blink_b)
	def output(self,txt):
		print('\r',txt,end='',sep='')

class ContinueOnEnter:
	def __init__(self):
		pass
	def tick(self,node,scene_manager,*a,**k):
		pass

class TitleScreen:
	def __init__(self):
		pass
	def tick(self,node,scene_manager,*a,**k):
		pass
