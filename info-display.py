import os
import time
import json
import requests
import datetime
from xml.etree import ElementTree

# TODO:
# display description, like/dislike, views, title, channel, listed status, date - done
# open appropriate file from vlc - done
# age limit display - done
# use duration_string from metadata, not VLC - done
# round RYD rating to x.x - done
# display tags and categories - done
# display video id and channel id when paused - done
# truncate subs to 1k 15k 15mil etc - done
# maybe display age of video
# * maybe display thumbnail as ascii art

# set defaults
last_track = ""
parsed_info = {}
last_paused = False

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
    global parsed_info
    parsed_info = {}
    try:
        with open(f"test/{video_id}.info.json", encoding="utf8") as file:
            info = file.read()
            info = json.loads(info)
            # check whether video was saved using return yt dislike metadata, kinda stupid?
            try:
                if info["RYD"]["response"]:
                    parsed_info["is_ryd"] = True
                    parsed_info["dislike_h"] = human_format(info.get("dislike_count"))
            except KeyError:
                parsed_info["is_ryd"] = False
                parsed_info["dislike_h"] = None
            parsed_info["description"] = info.get("description")
            parsed_info["like_h"] = human_format(info.get("like_count"))
            parsed_info["like"] = info.get("like_count")
            parsed_info["dislike"] = info.get("dislike_count")
            if info.get("average_rating"):
                parsed_info["rating"] = round(float(info.get("average_rating")), 1)
            else:
                parsed_info["rating"] = None
            parsed_info["views_h"] = human_format(info.get("view_count"))
            parsed_info["views"] = info.get("view_count")
            parsed_info["title"] = info.get("fulltitle")
            parsed_info["channel"] = info.get("uploader")
            parsed_info["handle"] = info.get("uploader_id")
            parsed_info["subs_h"] = human_format(info.get("channel_follower_count"))
            parsed_info["subs"] = info.get("channel_follower_count")
            parsed_info["published_status"] = info.get("availability")
            parsed_info["was_live"] = info.get("live_status")
            parsed_info["comments"] = info.get("comment_count")
            parsed_info["age"] = info.get("age_limit")
            parsed_info["duration"] = info.get("duration")
            parsed_info["id"] = info.get("id")
            parsed_info["c_id"] = info.get("channel_id")
            parsed_info["tags"] = info.get("tags")
            parsed_info["category"] = info.get("categories")
            # maybe we shouldn't assume that the date will always be 8 chars long; whatever
            parsed_info["upload_year"] = str(info.get("upload_date"))[0:4]
            parsed_info["upload_month"] = str(info.get("upload_date"))[4:6]
            parsed_info["upload_day"] = str(info.get("upload_date"))[6:8]
    except FileNotFoundError:
        parsed_info = False


# function to display the bits
# should it be formatted as
# Title: <title> or as
# <title>
def display_info(p, state):
    date = f'{p["upload_year"]}-{p["upload_month"]}-{p["upload_day"]}'  # date format
    # only print verbose if paused
    if state:
        print(f'{p["title"]} | {str(datetime.timedelta(seconds=int(p["duration"])))} | {p["views"]} views | {date} | {p["was_live"]}')
        if p["is_ryd"]:
            print(f'{p["channel"]} ({p["handle"]}) | {p["subs"]} subscribers | {p["like"]}L-{p["dislike"]}D (RYD) | {p["rating"]} stars')
        else:
            print(f'{p["channel"]} ({p["handle"]}) | {p["subs"]} subscribers | {p["like"]}L-{p["dislike"]}D | {p["rating"]} stars')
        print(f'{", ".join(p["category"])} | {p["published_status"]} | age limit: {p["age"]} | video ID: {p["id"]} | channel ID: {p["c_id"]}')
        print(", ".join(p["tags"]))
        print("\n" + p["description"])
    else:
        print(f'{p["title"]} | {str(datetime.timedelta(seconds=int(p["duration"])))} | {p["views_h"]} views | {date} | {p["was_live"]}')
        if p["is_ryd"]:
            print(f'{p["channel"]} ({p["handle"]}) | {p["subs_h"]} subscribers | {p["like_h"]} L - {p["dislike_h"]} D (RYD) | {p["rating"]} stars')
        else:
            print(f'{p["channel"]} ({p["handle"]}) | {p["subs_h"]} subscribers | {p["like_h"]} L - {p["dislike_h"]} D | {p["rating"]} stars')
        print(f'{", ".join(p["category"])} | {p["published_status"]} | age limit: {p["age"]} | video ID: {p["id"]}')
        print(", ".join(p["tags"]))
        # only print disc if paused
        print("pause to display verbose")
    print(str(p["comments"]) + " comments")


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
    # get duration, end, and volume:
    elapsed = tree.find('time').text
    duration = tree.find('length').text
    volume = tree.find('volume').text
    if tree.find("state").text == "playing":
        paused = False
    else:
        paused = True
    # load new video metadata
    if track_title != last_track:
        load_info(track_title)
        os.system('cls' if os.name == 'nt' else 'clear')
        if not parsed_info:
            print("Video has no info to display")
        else:
            display_info(parsed_info, paused)
        last_track = track_title
    elif paused != last_paused:
        # only update on play/pause
        os.system('cls' if os.name == 'nt' else 'clear')
        display_info(parsed_info, paused)
        last_paused = paused

    time.sleep(0.5)
