import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GstNet, GObject
from sys import argv
import time
from see import see
import struct
from socket import *
from threading import Thread

def broadcast_current_time(pipeline):
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    while True:
        success, nanoseconds = pipeline.query_position(Gst.Format.TIME)
        playing_state = pipeline.get_state(timeout=Gst.CLOCK_TIME_NONE)
        msg = struct.pack("!Qi", nanoseconds, playing_state[1])
        sock.sendto(msg, ('255.255.255.255', 1985))        
        print((success, nanoseconds))
        time.sleep(1)

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

broadcaster = Thread(target=broadcast_current_time,
                     kwargs={"pipeline":pipeline},
                     daemon=True)
broadcaster.start()

pipeline.set_state(Gst.State.PLAYING)
for x in range(120):
    time.sleep(1)
#    if x == 30:
#        pipeline.set_state(Gst.State.PAUSED)
#    if x == 35:
#        pipeline.set_state(Gst.State.PLAYING)

pipeline.set_state(Gst.State.NULL)

