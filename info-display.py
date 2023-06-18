import os
import time
import json
import requests
from xml.etree import ElementTree

# TODO:
# display description, like/dislike, views, title, channel, listed status, date
# open appropriate file from vlc
# * maybe display thumbnail as ascii art

# set defaults

# load vlc password from password.txt
with open('password.txt') as file_pw:
    vlc_password = file_pw.read()

# function to load infojson from video id, and split it into appropriate bits

# function to display the bits

# mainloop
while True:
    # get track xml from vlc
