# yt-dlp-tools
a collection of tools for viewing json files downloaded by yt-dlp

- chat-player
  - displays chat replay in sync with a video playing in VLC
- comment-viewer
  - displays comments, replies, and likes. hopefully. 
- info-display
  - displays description, likes/dislikes, views, 


you will need to enable VLC's http server, and set a password. put the password in a file named password.txt

files should be in a folder, named as follows, with \<id> being the video's ID (after the watch?v= part):
```
<id>.<video>
<id>.description (optional)
<id>.info.json
<id>.live_chat.json
```


---
this is just for my personal video archive. i may make the code better someday. but not today.