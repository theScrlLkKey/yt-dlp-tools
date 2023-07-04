import os
import time
import json
import requests
import datetime
from datetime import datetime as dt
from xml.etree import ElementTree

# TODO:
# display comments, replies, likes
# open appropriate file from vlc
# interactive?

# set defaults
last_track = ""
comments = {}

# load vlc password from password.txt
with open('password.txt') as file_pw:
    vlc_password = file_pw.read()


def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


# function to load infojson from video id, and split it into appropriate bits
def load_info(video_id):
    global comments
    comments = {}
    try:
        with open(f"test/{video_id}.info.json", encoding="utf8") as file:
            info = file.read()
            info = json.loads(info)
            comments = info["comments"]
    except FileNotFoundError:
        comments = False


def display_comments():
    for comment in comments:
        print(comment["like_count"], comment["author"], comment["parent"], comment["text"])


# connect to vlc, parse xml to get currently playing video ID
vlc_session = requests.Session()
vlc_session.auth = ('', vlc_password)  # Username is blank, just provide the password

# mainloop
while True:
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
    if tree.find("state").text == "playing":
        paused = False
    else:
        paused = True
    # load new video metadata
    if track_title != last_track:
        load_info(track_title)
        os.system('cls' if os.name == 'nt' else 'clear')
        if not comments:
            print("Video has no info to display")
        else:
            display_comments()
        last_track = track_title
    # elif paused != last_paused and parsed_info:
    #     # only update on play/pause
    #     os.system('cls' if os.name == 'nt' else 'clear')
    #     display_info(parsed_info, paused)
    #     last_paused = paused

    time.sleep(0.5)
