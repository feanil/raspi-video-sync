import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GstNet, GObject
from sys import argv
import time
from see import see
import struct
from socket import *
from threading import Thread
import zmq
import json

next_loop = False
context = zmq.Context()

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
    global next_loop
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:5891")
    socket.setsockopt_string(zmq.SUBSCRIBE, 'DDP')
    while True:
        # Recv messages
        raw_string = socket.recv_string()
        json_string = raw_string[4:]
        message = json.loads(json_string) 
        # Unpack json
        if message['action'] == 'PLAY':
            pipeline.set_state(Gst.State.PLAYING)
        elif message['action'] == 'PAUSE':
            pipeline.set_state(Gst.State.PAUSED)
        elif message['action'] == 'SEEK':
            seek(pipeline, message['time'])
        elif message['action'] == 'NEXT':
            next_loop = True

def close(current, target):
    seconds_threshold = .1
    
    nano_threshold = int(seconds_threshold * 1e9)
    if (target - current) < nano_threshold:
        return True
    else:
        return False

def monitor_movie(pipeline):
    global next_loop
    # Read in the start and end times for each loop.
    times = [] # TODO: load in times.
    times = [
        {'start': 20000000000, 'end': 30000000000},
    ]
    iter_times = iter(times)
    if len(times) == 0:
        print("No timecodes.")
        return

    current_loop = next(iter_times)
    monitor = True
    while monitor:
        success, nanoseconds = pipeline.query_position(Gst.Format.TIME)
        if close(nanoseconds, current_loop['end']):
            seek(pipeline, current_loop['start'])
        if next_loop:
            try:
                current_loop= next(iter_times)
                next_loop = False
            except StopIteration:
                # Stop the monitor loop after the last time set.
                monitor = False
        time.sleep(.05)

    print("Monitor stopping.")

GObject.threads_init()
Gst.init(None)
# Get video location
video = "/home/feanil/src/pndp/videos/old/movie.mp4"
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

loop_monitor = Thread(target=monitor_movie,
                      kwargs={"pipeline": pipeline},
                      daemon=True)
loop_monitor.start()

zmq_control = Thread(target=zmq_listener,
                     kwargs={"pipeline": pipeline},
                     daemon = True)
zmq_control.start()

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

