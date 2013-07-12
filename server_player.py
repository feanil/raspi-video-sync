import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GstNet, GObject
from sys import argv
import time
from see import see
import struct
from socket import *
from threading import Thread

end_loop = False

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

def seek(pipeline, time):
    pipeline.seek_simple(
        Gst.Format.TIME,
        Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
        time)

#TODO:  A thread for listening to zmq messages
def zmq_listener(pipeline):
    while True:
        # Recv messages
        # Unpack json
        if message['action'] == 'PLAY':
            pass
        elif message['action'] == 'PAUSE':
            pass
        elif message['action'] == 'SEEK':
            seek(pipeline, message['time'])
        elif message['action'] == 'NEXT':
            end_loop = True

def loop(pipeline, start, end, first_run):
    # Seek to the time provided.
    # seek to start.
    seek(pipeline, start)

    if first_run:
        end_loop = False

    if end_loop == False:
        # TODO: get this worked out
        gst_clock_id_wait_async( end, loop, (pipeline, start, end, False))

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

# Read in the start and end times for each loop.
times = []# TODO: Read in start and end times.
for item in times:
    start = item['loop_start']
    end = item['loop_end']

    # TODO: Figure out the correct call.
    gst_clock_id_wait_async( end, loop, (pipeline, start, end, True))
    
    

pipeline.set_state(Gst.State.PLAYING)
#for x in range(120):
#    time.sleep(1)
#    if x == 30:
#        pipeline.set_state(Gst.State.PAUSED)
#    if x == 35:
#        pipeline.set_state(Gst.State.PLAYING)
try:
    while True:
        time.sleep(1)
finally:
    pipeline.set_state(Gst.State.NULL)

