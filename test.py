import json

with open("subtitles.json", "r") as file:
    data = json.load(file)

for subtitle in data:
    if subtitle['video_slow_down'] != 1:
        subtitle['video_slow_down'] += 1

with open("subtitles.json", "w") as file:
    json.dump(data, file)