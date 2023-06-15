import vlc
import time
import json
from datetime import timedelta

# TODO: use windows media api instead of screwing around with vlc? can i make a VLC plugin? i want to attach to an existing vlc instance

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
            else:  # do not display pre chat
                total_seconds = -1
                # print("[PRE", chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"][ "authorName"]["simpleText"], "]",chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["message"]["runs"][0]["text"])
            chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["timestampText"]["parsed"] = total_seconds
            chat_data.append(chat_message)
        except KeyError:
            # Handle missing keys or other errors
            print("Skipping chat message due to missing keys:", chat_message)


# Callback function to display chat messages
def display_content(event):
    current_time = event.u.new_time  # milliseconds

    # Display chat messages
    for chat_message in chat_data:
        try:
            chat_timestamp = int(chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["timestampText"]["parsed"])
            # print(str(chat_timestamp) + " " + str(current_time/1000))
            if chat_timestamp <= current_time/1000:
                print("[", chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["authorName"]["simpleText"], "]", chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["message"]["runs"][0]["text"])
                chat_data.pop(chat_data.index(chat_message))  # disable to allow rewinding, will re print screen every time however
        except KeyError:
            # Handle missing keys or other errors
            # print("Skipping chat message due to missing keys:", chat_message)
            # bots/donos
            pass


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
