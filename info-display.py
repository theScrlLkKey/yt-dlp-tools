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

# load vlc password from password.txt
with open('password.txt') as file_pw:
    vlc_password = file_pw.read()

# function to load infojson from video id, and split it into appropriate bits
def load_info(video_id):
    # reset variables

    # open file



# function to display the bits

# mainloop
while True:
    # get status xml from vlc, parse to ID (use chat player code)

    # is it the same ID? sleep or update

    # otherwise, load new video metadata

    time.sleep(0.01)