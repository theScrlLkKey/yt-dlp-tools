import os
import time
import json
import requests
from xml.etree import ElementTree

# TODO:
# display description, like/dislike, views, title, channel, listed status, date
# open appropriate file from vlc
# * maybe display thumbnail as ascii art
# show video progress and volume with ascii blocks

# set defaults
last_track = ""

# load vlc password from password.txt
with open('password.txt') as file_pw:
    vlc_password = file_pw.read()


# function to load infojson from video id, and split it into appropriate bits
def load_info(video_id):
    try:
        with open(f"test/{video_id}.info.json", encoding="utf8") as file:
            info = file.read()
            info = json.loads(info)
            print(info)
            # parse infojson
    except FileNotFoundError:
        print("Video has no chat to replay")
        # ensure program won't close


# function to display the bits
def display_info(progress, end, vol):
    pass


# mainloop
while True:
    # connect to vlc, parse xml to get currently playing video ID
    vlc_session = requests.Session()
    vlc_session.auth = ('', vlc_password)  # Username is blank, just provide the password
    try:
        raw_xml = vlc_session.get('http://localhost:8080/requests/status.xml', verify=False)
    except requests.exceptions.ConnectionError:
        print("VLC not running. Please open a video first.")
        exit()
    # parse xml
    tree = ElementTree.fromstring(raw_xml.content)
    track_title = tree.find('information').find('category[@name="meta"]').find('info[@name="PURL"]')
    if track_title is None:
        time.sleep(2)
        continue
    # yoink video id from url
    track_title = track_title.text.split('/')[-1].replace('watch?v=', '')
    # get duration, end, and volume:

    # load new video metadata
    if track_title != last_track:
        load_info(track_title)
        last_track = track_title
    # otherwise, it is the same ID sleep or update
    else:
        # run display info, but for now, sleep
        # display_info()
        pass

    time.sleep(0.5)
