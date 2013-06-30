import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GstNet, GObject
from sys import argv
import time

GObject.threads_init()                                                   
Gst.init(None)

# Get video location
video = "/home/pi/ddp/movie.mp4"
if len(argv) > 1:
  video = argv[1]

# Setup Pipeline
pipeline = Gst.Pipeline()
playbin = Gst.ElementFactory.make('playbin',None)
pipeline.add(playbin)
playbin.set_property('uri','file://' + video)

# Create a network clock
client_clock = GstNet.NetClientClock(address="192.168.1.107")
print("Client Clock: {}".format(client_clock))
pipeline.use_clock(client_clock)
pipeline.set_state(Gst.State.PLAYING)
print("Client Clock: {}".format(pipeline.get_clock()))
print("Client Clock: {}".format(pipeline.get_clock()))
time.sleep(30)
pipeline.set_state(Gst.State.NULL)


