import os
import time
import json
import requests
from datetime import timedelta

# TODO: use windows media api instead of screwing around with vlc? can i make a VLC plugin? i want to attach to an existing vlc instance
# grab current elapsed time from VLC web XML doc, then feed that in.
# get title, if title changes change file we are reading from
# maybe attempt to compensate for lag, offset is included in live chat json

chat_data = []


def load_chat(video_id):
    global chat_data
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
                    # print("[PRE", chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"][ "authorName"]["simpleText"], "]",chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["message"]["runs"][0]["text"])

                chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["timestampText"]["parsed"] = total_seconds
                chat_data.append(chat_message)
            except KeyError:
                # Handle missing keys or other errors
                print("Skipping chat message due to missing keys:", chat_message)


# Callback function to display chat messages
def display_content(seconds):
    global last_time
    global chat_data
    current_time = int(seconds)  # seconds

    # on rewind, clear screen and refill chat messages
    if current_time < last_time:
        chat_data = chat_data_clean
        os.system('cls' if os.name == 'nt' else 'clear')
    # Display chat messages
    for chat_message in chat_data:
        try:
            chat_timestamp = int(chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["timestampText"]["parsed"])
            # print(str(chat_timestamp) + " " + str(int(current_time/1000)))
            if chat_timestamp <= current_time:
                print("[", chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["timestampText"]["simpleText"], chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["authorName"]["simpleText"], "]", chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["message"]["runs"][0]["text"])
                chat_data.pop(chat_data.index(chat_message))
        except KeyError:
            # Handle missing keys or other errors
            # print("Skipping chat message due to missing keys:", chat_message)
            # bots/donos
            pass
    last_time = current_time


chat_data_clean = chat_data
last_time = 0

# connect to vlc, parse xml to get currently playing video

# Load the JSON chat data

# mainloop
while True:
    # get xml

    # parse xml, get duration, title

    # switch file,

    # Wait for a small duration
    time.sleep(0.1)
