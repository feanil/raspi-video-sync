import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GstNet, GObject
from sys import argv
import time
import math
from threading import Thread
import socket
import struct

GObject.threads_init()                                                   
Gst.init(None)

UDP_IP= "<broadcast>"
UDP_PORT= 1985

def seek(pipeline, time):
    pipeline.seek_simple(
        Gst.Format.TIME,
        Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
        time)

def monitor_position(pipeline):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        data, addr = sock.recvfrom(100)
        position, state = struct.unpack('!Qi',data)
        success, local_position = pipeline.query_position(Gst.Format.TIME)
        difference = local_position - position

        if state == Gst.State.PAUSED:
            pipeline.set_state(Gst.State.PAUSED)
        elif state == Gst.State.PLAYING:
            pipeline.set_state(Gst.State.PLAYING)

            if difference > 2500000000:
                # we are ahead, pause and wait.
                seek(pipeline, position)
                print("Seeking back to {}".format(position))
            elif difference < -2500000000:
                # we are behind, jump forward.
                seek(pipeline, position)
                print("Seeking forward to {}".format(position))

# Get video location
video = "/home/pi/ddp/movie.mp4"
if len(argv) > 1:
  video = argv[1]

# Setup Pipeline
pipeline = Gst.Pipeline()
playbin = Gst.ElementFactory.make('playbin',None)
pipeline.add(playbin)
playbin.set_property('uri','file://' + video)

# Start monitoring for the master.
receiver = Thread(target=monitor_position,
                  kwargs={"pipeline": pipeline})
receiver.daemon = True
receiver.start()

# Create a network clock
pipeline.set_state(Gst.State.PLAYING)
while True:
    time.sleep(1)

pipeline.set_state(Gst.State.NULL)
