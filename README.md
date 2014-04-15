#pyscene

##MetaEvent
The MetaEvent object has a single field, 'handlers',
which is a list of callback functions called by the
instance's __call__ method. Uses args and kwargs to
reflect similar calls across all callbacks.

##Promise
A Promise object is used to provide a definite way
to ensure things are called in a certain order.

##Deferred
This is used to ensure Promise objects are only
triggered once per event.

##ModuleCache
The ModuleCache is used only in a static context,
and is used to dynamically load objects from modules
in a dynamic, run-time environment.

##SceneNode
This is where the most magic happens. This is set up
to bind JSON data to dynamic run-time objects. A Node
has sub_nodes, a type, and the args / kwargs fields
will be passed to the run-time type's __init__ method.

##SceneScope
A SceneScope is used to control how often certain nodes
need to be ticked. A value of 0 means the node is paused,
if the node's path isn't present in the scope, it's considered
to be stopped. Otherwise, a value of 1 means execute every
tick, a value of 2 means every other frame, and so forth.

##SceneManager
SceneManagers handle transitions to and from different
scenes, as well as being the object to call every frame.
