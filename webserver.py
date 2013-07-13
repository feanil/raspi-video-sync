import cherrypy
import zmq
import json

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5891")

class Base(object):

    @cherrypy.expose
    def index(self):
        return open('index.html').read()

    @cherrypy.expose
    def pause(self):
        message = {'action': 'PAUSE'}
        self.send_message(message)

    @cherrypy.expose
    def play(self):
        message = {'action': 'PLAY'}
        self.send_message(message)

    @cherrypy.expose
    def next(self):
        message = {'action': 'NEXT'}
        self.send_message(message)

    def send_message(self, message):
        raw_message = json.dumps(message)
        socket.send_string("DDP {}".format(raw_message)) 
        print("Sending {}.".format(message))
        raise cherrypy.HTTPRedirect("/") 

cherrypy.config.update({'server.socket_host': '0.0.0.0'})
cherrypy.quickstart(Base())
