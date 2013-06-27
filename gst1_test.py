import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject
from sys import argv
import time

GObject.threads_init()                                                   
Gst.init(None)

pipeline = Gst.Pipeline()

playbin = Gst.ElementFactory.make('playbin',None)
pipeline.add(playbin)
playbin.set_property('uri','file://' + argv[1])
pipeline.set_state(Gst.State.PLAYING)
time.sleep(30)
pipeline.set_state(Gst.State.NULL)
