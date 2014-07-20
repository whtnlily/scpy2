# -*- coding: utf-8 -*-

import inspect

def issimple(obj):
    return isinstance(obj, (str, unicode, int, long, float))

def isempty(obj):
    if obj is None:
        return True
    if isinstance(obj, list) and obj == []:
        return True
    return False

def isproperty(obj, attr):
    try:
        return isinstance(getattr(obj.__class__, attr), property)
    except:
        return False

class Graphviz(object):

    def node(self, obj):
        if isempty(obj): return
        self.visited_obj.append(obj)
        if type(obj) in (list, tuple):
            label="|".join("<f%d> %s" % (i, repr(v) if issimple(v) else "*") for i, v in enumerate(obj))
            color = "gray"
        elif type(obj) is dict:
            label="|".join("<f%s> %s" % (key, str(key) + ":" + repr(val) 
                                         if issimple(val) else key) for key, val in obj.items())
            color = "gray"            
        else:
            label = obj.__class__.__name__
            color = "white"
        text = 'obj_%d[label="%s",fillcolor=%s];' % (id(obj), label, color)
        self.result.append(text)
    
    def link(self, obj1, obj2, attr, is_property=False):
        if isempty(obj2): return
        style = "dashed" if is_property else "solid"
        text = 'obj_%d -> obj_%d[label="%s",style=%s];' % (id(obj1), id(obj2), attr, style)
        self.result.append(text)
        if issimple(obj2):
            text = 'obj_%d[label="%s", fillcolor=white]' % (id(obj2), repr(obj2))
            self.result.append(text)

    def list_link(self, alist, idx, obj):
        if isempty(obj): return
        if issimple(obj): return
        text = "obj_%d:f%d -> obj_%d;" % (id(alist), idx, id(obj))
        self.result.append(text)
        
    def dict_link(self, adict, key, obj):
        if isempty(obj): return
        if issimple(obj): return
        text = "obj_%d:f%s -> obj_%d;" % (id(adict), key, id(obj))
        self.result.append(text)

    def __init__(self):
        self.checked_ids = set()
        self.expanded = set()
        self.visited_obj = []

    def _graphviz(self, obj):
        if obj is None: return
        if id(obj) in self.checked_ids: return
        if issimple(obj): return        
        self.node(obj)
        self.checked_ids.add(id(obj))
        if type(obj) in (list, tuple):
            for idx, inner in enumerate(obj):
                self._graphviz(inner)
                self.list_link(obj, idx, inner)
            return
        if type(obj) is dict:
            for key, inner in obj.iteritems():
                self._graphviz(inner)
                self.dict_link(obj, key, inner)
            return            
            
        class_names = set([cls.__name__ for cls in obj.__class__.mro()])
        klass = obj.__class__.__name__
        if (len(class_names & self.expand_classes) > 0 or 
           klass in self.expand_once_classes and klass not in self.expanded):
            self.expanded.add( klass )
            for attr in self.check_attributes:
                    if hasattr(obj, attr):
                        subobj = getattr(obj, attr)
                        if inspect.isroutine(subobj):
                            continue
                        self._graphviz(subobj)
                        self.link(obj, subobj, attr, isproperty(obj, attr))
                        
    @classmethod                    
    def graphviz(klass, obj):
        self = klass()
        self.checked_ids = set()
        self.expanded = set()
        self.result = [
        """digraph structs {
rankdir="LR";        
node [shape=record,style=filled];
edge [fontsize=10, penwidth=0.5];"""
        ]
        self._graphviz(obj)
        self.result.append("}")
        return "\n".join(self.result)

        
class GraphvizDataFrame(Graphviz):
    
    check_attributes = ["index", "columns", "values", "name", "_data", 
                        "blocks", "shape", "_engine", "mapping"]
    
    expand_classes = {"tuple"}
    expand_once_classes = {"Index", "DataFrame", "BlockManager", 
                           "FloatBlock", "ObjectBlock", "ObjectEngine"}

    
class GraphvizMatplotlib(Graphviz):
    
    check_attributes = [
        "patch", "axes", "lines", "patches", "texts", "artists", 
        "xaxis", "yaxis", "majorTicks", "label", "tick1line", "tick2line"
    ]
    
    expand_classes = {"Figure", "Axes", "Line2D", "Text"}
    expand_once_classes = {"XAxis", "YAxis",  "XTick", "YTick"}