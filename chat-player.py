import os
import vlc
import time
import json
from datetime import timedelta

# TODO: use windows media api instead of screwing around with vlc? can i make a VLC plugin? i want to attach to an existing vlc instance
# grab current elapsed time from VLC web XML doc, then feed that in. dont pop from list
# get title, if title changes change file we are reading from
# maybe attempt to compensate for lag, offset is included in live chat json

# get video ID from user
video_id = input('Video ID:  ')

# Create a VLC player instance
instance = vlc.Instance()
player = instance.media_player_new()

# Load the MKV video
media = instance.media_new(f"test/{video_id}.mkv")
player.set_media(media)

# Load the JSON chat data
chat_data = []
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

chat_data_clean = chat_data
last_time = 0


# Callback function to display chat messages
def display_content(event):
    global last_time
    global chat_data
    current_time = event.u.new_time  # milliseconds

    # on rewind, clear screen and refill chat messages
    if current_time < last_time:
        chat_data = chat_data_clean
        os.system('cls' if os.name == 'nt' else 'clear')
    # Display chat messages
    for chat_message_func in chat_data:
        try:
            chat_timestamp = int(chat_message_func["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["timestampText"]["parsed"])
            # print(str(chat_timestamp) + " " + str(int(current_time/1000)))
            if chat_timestamp <= current_time/1000:
                print("[", chat_message_func["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["timestampText"]["simpleText"], chat_message_func["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["authorName"]["simpleText"], "]", chat_message_func["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["message"]["runs"][0]["text"])
                chat_data.pop(chat_data.index(chat_message_func))
        except KeyError:
            # Handle missing keys or other errors
            # print("Skipping chat message due to missing keys:", chat_message)
            # bots/donos
            pass
    last_time = current_time


# Register the callback function
event_manager = player.event_manager()
event_manager.event_attach(vlc.EventType.MediaPlayerTimeChanged, display_content)

# Start playing the video
player.play()

while True:
    # Check if the player is still playing
    if player.get_state() == vlc.State.Ended:
        break

    # Wait for a small duration
    time.sleep(0.1)

# Release the player resources
player.release()
