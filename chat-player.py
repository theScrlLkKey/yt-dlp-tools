import os
import time
import json
import requests
from datetime import timedelta
from xml.etree import ElementTree
from collections import deque

# TODO:
# grab current elapsed time from VLC web XML doc, then feed that in. - done
# get title, if title changes change file we are reading from
# maybe attempt to compensate for lag, offset is included in live chat json
# display donations liveChatPaidMessageRenderer and paid_message (check for existance of liveChatTextMessageRenderer, then check for other types)

chat_data_clean = []
chat_data = deque()

last_time = 0

# load vlc password from password.txt
with open('password.txt') as file_pw:
    vlc_password = file_pw.read()


def load_chat(video_id):
    global chat_data
    global chat_data_clean
    try:
        with open(f"test/{video_id}.live_chat.json", encoding="utf8") as file:
            for line in file:
                chat_message = json.loads(line)
                try:
                    timestamp_text = chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["timestampText"]["simpleText"]
                    if "-" not in timestamp_text:
                        timestamp_hour, timestamp_min_sec = timestamp_text.split(':', 1)  # split into hour and minsec
                        if ":" in timestamp_min_sec:
                            timestamp_min, timestamp_sec = timestamp_min_sec.split(':')  # try to split further
                        else:
                            # not yet into hours, fix it
                            timestamp_min = timestamp_hour
                            timestamp_sec = timestamp_min_sec
                            timestamp_hour = "0"
                        total_seconds = timedelta(
                            hours=int(timestamp_hour),
                            minutes=int(timestamp_min),
                            seconds=int(timestamp_sec)
                        ).total_seconds()
                    else:  # display pre-chat
                        total_seconds = -1
                    chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["timestampText"]["parsed"] = int(total_seconds)
                    chat_data.append(chat_message)
                except KeyError:
                    # Handle missing keys or other errors
                    print("Skipping chat message due to missing keys:", chat_message)
        chat_data_clean = chat_data.copy()
    except FileNotFoundError:
        print("Video has no chat to replay")


# function to display chat messages
def display_content(seconds):
    global last_time
    global chat_data
    current_time = int(seconds)  # seconds
    messages_to_print = []

    # on rewind, clear screen and refill chat messages
    if current_time < last_time:
        chat_data = chat_data_clean.copy()
        os.system('cls' if os.name == 'nt' else 'clear')

    # Display chat messages
    for index, chat_message in enumerate(chat_data):
        standard_message = chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]
        timestamp_text = standard_message["timestampText"]["simpleText"]
        author_name = standard_message["authorName"]["simpleText"]
        # this is a really impressive performance improvement from a bunch of nested try/catch, dont do that
        # there may be other types than text or emoji... unsure
        message_text = "".join(run.get("text", "") or run["emoji"].get("emojiId", "") for run in standard_message["message"]["runs"])
        chat_timestamp = standard_message["timestampText"]["parsed"]

        if chat_timestamp <= current_time:
            messages_to_print.append((timestamp_text, author_name, message_text))
        else:
            break

    # Print chat messages, then remove them
    for timestamp_text, author_name, message_text in messages_to_print:
        print("[", timestamp_text, author_name, "]", message_text)
        # this should work fine. it feels slightly wrong though?
        chat_data.popleft()

    # update previous time
    last_time = current_time


# connect to vlc, parse xml to get currently playing video
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
# yoink video id from url
track_title = track_title.text.split('/')[-1].replace('watch?v=', '')

# Load the JSON chat data
load_chat(track_title)

# Convert chat_data and chat_data_clean to deque
# the docs for deque makes it seem like this is good? probably shouldnt trust chatgpt blindly
chat_data = deque(chat_data)
chat_data_clean = deque(chat_data_clean)

# mainloop
while True:
    # get xml
    try:
        raw_xml = vlc_session.get('http://localhost:8080/requests/status.xml', verify=False)
    except requests.exceptions.ConnectionError:
        print("VLC has closed.")
        exit()
    # parse xml, get duration, title
    tree = ElementTree.fromstring(raw_xml.content)
    track_title_current = tree.find('information').find('category[@name="meta"]').find('info[@name="PURL"]')
    elapsed = tree.find('time')
    # yoink video id from url
    track_title_current = track_title_current.text.split('/')[-1].replace('watch?v=', '')
    # switch file if it has switched
    if track_title_current != track_title:
        load_chat(track_title_current)
        track_title = track_title_current
        display_content(0)
    else:
        # print chat message for timestamp
        display_content(elapsed.text)
        # Wait for a small duration
        time.sleep(0.01)
