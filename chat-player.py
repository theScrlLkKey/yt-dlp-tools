import vlc
import time
import json
from datetime import datetime, timedelta

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
            timestamp = datetime.strptime(timestamp_text, "%H:%M:%S")
            total_seconds = timedelta(
                hours=timestamp.hour,
                minutes=timestamp.minute,
                seconds=timestamp.second
            ).total_seconds()
            chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["timestampText"]["simpleText"] = total_seconds
            chat_data.append(chat_message)
        except KeyError:
            # Handle missing keys or other errors
            print("Skipping chat message due to missing keys:", chat_message)
        except ValueError:
            # we cannot account for pre-chat
            print("Skipping chat message, pre-chat:", chat_message)


# Callback function to display chat messages
def display_content(event):
    current_time = event.u.new_time

    # Display chat messages
    for chat_message in chat_data:
        input(chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["timestampText"]["simpleText"])
        input(current_time)
        if chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["timestampText"]["simpleText"] <= current_time:
            try:
                print("[", chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["authorName"]["simpleText"], "]", chat_message["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["message"]["runs"][0]["text"])
            except KeyError:
                # Handle missing keys or other errors
                print("Skipping chat message due to missing keys:", chat_message)


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
