import os
import time
import json
import requests
from datetime import timedelta
from xml.etree import ElementTree

# TODO:
# grab current elapsed time from VLC web XML doc, then feed that in. - done
# get title, if title changes change file we are reading from
# maybe attempt to compensate for lag, offset is included in live chat json
# allow video switching without reloading the program
# display donations

chat_data_clean = []
chat_data = []

# load vlc password from password.txt
with open('password.txt') as file:
    vlc_password = file.read()


def load_chat(video_id):
    global chat_data
    global chat_data_clean
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
                chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["timestampText"]["parsed"] = total_seconds
                chat_data.append(chat_message)
            except KeyError:
                # Handle missing keys or other errors
                print("Skipping chat message due to missing keys:", chat_message)
    chat_data_clean = chat_data.copy()
    # input(chat_data_clean)


# Callback function to display chat messages
def display_content(seconds):
    global last_time
    global chat_data
    current_time = int(seconds)  # seconds
    indexes_remove = []

    # on rewind, clear screen and refill chat messages
    if current_time < last_time:
        chat_data = chat_data_clean.copy()
        os.system('cls' if os.name == 'nt' else 'clear')

    # Display chat messages
    for chat_message in chat_data:
        try:
            # get timestamp in seconds
            chat_timestamp = int(chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["timestampText"]["parsed"])
            # if chat message should be displayed, print it, and the add it into the index of messages we have printed
            if chat_timestamp <= current_time:
                # because youtube is actually stupid, messages with emojis are split into
                # ["message"]["runs"][0]["text"] ["message"]["runs"][1]["emoji"]["emojiId"] etc
                message_run_itr = 0
                message_parsed = ""
                # not super great code here
                for i in range(len(chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["message"]["runs"])):
                    try:
                        message_parsed += chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["message"]["runs"][i]["text"]
                    except KeyError:
                        try:
                            message_parsed += chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["message"]["runs"][i]["emoji"]["emojiId"]
                        except KeyError:
                            input("something other than emoji or text?")
                            print(message_parsed)
                            exit()
                print("[", chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["timestampText"]["simpleText"], chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["authorName"]["simpleText"], "]", message_parsed)
                indexes_remove.append(int(chat_data.index(chat_message)))
            else:
                # now we have printed all the current messages, so we remove them
                for i in sorted(indexes_remove, reverse=True):
                    del chat_data[i]
                break
        except KeyError as err:
            # Handle missing keys or other errors
            # print("Skipping chat message due to missing keys:", chat_message)
            # bots/donos? unsure
            # attempt to print paid message
            try:
                # get timestamp in seconds
                input(chat_message)
                chat_timestamp = int(chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatPaidMessageRenderer"]["timestampText"]["parsed"])
                print("got here")
                # if chat message should be displayed, print it, and the add it into the index of messages we have printed
                if chat_timestamp <= current_time:
                    print("[", chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatPaidMessageRenderer"]["timestampText"]["simpleText"], chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatPaidMessageRenderer"]["purchaseAmountText"]["simpleText"], chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatPaidMessageRenderer"]["authorName"]["simpleText"], "]", chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatPaidMessageRenderer"]["message"]["runs"][0]["text"])
                    indexes_remove.append(int(chat_data.index(chat_message)))
            except KeyError as err:
                # welp, guess it wasn't a dono
                pass

    last_time = current_time


last_time = 0

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
        elapsed = 0
    # print chat message for timestamp
    display_content(elapsed.text)
    # Wait for a small duration
    time.sleep(0.1)
