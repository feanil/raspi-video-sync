raspi-video-sync
================

Sync playback of videos for a RaspberryPi Video Wall

I need to make a video wall for an art project.  We had a train car set and I used 4 raspberry pis to power four displays that acted as windows in the train.  They needed to play different videos in sync with each other.  The code here sets up the Pis with all the libraries needed to use gstreamer to play back video on the RaspberryPis.

#### Why Gstreamer?

I chose gstreamer because it takes advantage of the hardware decoding of the video and provided a good APIso that I could control the videos from python.

Components
==========

### Clients
The clients reside on the RaspberryPis, they playback their respective videos and listen to broadcasts of timecodes and state.  If there are timecodes, it will sync to them.

### Server
The basic idea of this player is that it looks at loops.json and loops between a set of time codes.  When it receives a signal it continues to play through to the next loop interval.

The server can also recieve a few other signal types which can be sent from the remote.

### Remote
If you want to remotely control the videos or skip around in them then start up the remote which is a webserver.  You can go to the website to go to the control.  The remote controls going to different sections as defined in sections.json and going to different loos as defined in loops.json

### Ansible
I use ansible to provision the raspberry pis with all the libraries they need and to start up the players in sync.

```

cd playbooks
ansible-playbook -i inventory.ini setup.yml --tags="copy_movie"
ansible-playbook -i inventory.ini setup.yml --tags="setup" --extra-vars="one_time=true"
ansible-playbook -i inventory.ini setup.yml --tags="setup" --extra-vars="one_time=true"
ansible-playbook -i inventory.ini setup.yml --tags="play"

# In a seperate window
python server_player.py

# In a third window
python webserver.py
firefox localhost:5981

```
