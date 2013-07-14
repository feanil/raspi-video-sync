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
loop_index = 0
context = zmq.Context()
loop_times = []
section_times = []

# Read in the start and end times for each loop.
def nano(timestamp):
    minute, sec = timestamp.split(':')
    all_seconds = int(minute)*60 + int(sec)
    return all_seconds*1e9

def get_section_times(filename="sections.json"):
    section_times = []
    human_loop = json.load(open(filename))
    for item in human_loop:
        section_times.append(nano(item))
    return section_times

def get_loop_times(filename='loops.json'):
    loop_times = []
    human_loops = json.load(open(filename))
    for item in human_loops:
        greadable = {}
        for k,v in item.items():
            greadable[k] = nano(v)
        loop_times.append(greadable)

    return loop_times

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
    global loop_index
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
            print('Got Next.')
            loop_index += 1
            loop_index %= len(loop_times)
        elif message['action'] == 'NEXT_LOOP':
            loop_index += 1
            loop_index %= len(loop_times)
            seek(pipeline, loop_times[loop_index]['start'])
        elif message['action'] == 'PREV_LOOP':
            loop_index -= 1
            loop_index %= len(loop_times)
            seek(pipeline, loop_times[loop_index]['start'])
        elif message['action'] == 'PREV_SECTION':
            print("Prev Section")
            seek(pipeline, section_times[loop_index])

def close(current, target):
    seconds_threshold = .1
    
    nano_threshold = int(seconds_threshold * 1e9)
    if (target - current) < nano_threshold:
        return True
    else:
        return False

def monitor_movie(pipeline):
    global loop_index
    global loop_times

    if len(loop_times) == 0:
        print("No timecodes.")
        return

    monitor = True
    while monitor:
        current_loop = loop_times[loop_index]
        success, nanoseconds = pipeline.query_position(Gst.Format.TIME)
        if close(nanoseconds, current_loop['end']):
            seek(pipeline, current_loop['start'])
        time.sleep(.05)

    print("Monitor stopping.")

loop_times = get_loop_times()
section_times = get_section_times()

GObject.threads_init()
Gst.init(None)
# Get video location
video = "/home/feanil/src/pndp/videos/movie0.mov"
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
try:
    while True:
        time.sleep(1)
finally:
    pipeline.set_state(Gst.State.NULL)

