import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GstNet, GObject
from sys import argv
import time
from see import see

GObject.threads_init()
Gst.init(None)
# Get video location
video = "/home/feanil/src/pndp/movie.mp4"
if len(argv) > 1:
  video = argv[1]

# Setup Pipeline
pipeline = Gst.Pipeline()
playbin = Gst.ElementFactory.make('playbin',None)
pipeline.add(playbin)
playbin.set_property('uri','file://' + video)

# Create a network clock
base_clock = pipeline.get_clock()
net_clock = GstNet.NetTimeProvider(clock=base_clock)
print("Net Clock: {} {} {}".format(net_clock.get_property('clock'), net_clock.get_property('active'),net_clock.get_property('address')))
pipeline.use_clock(base_clock)

pipeline.set_state(Gst.State.PLAYING)
print(pipeline.get_clock())
time.sleep(60)
pipeline.set_state(Gst.State.NULL)
