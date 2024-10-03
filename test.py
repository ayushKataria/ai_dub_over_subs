import json

with open("subtitles.json", "r") as file:
    subtitles = json.load(file)

for subtitle in subtitles:
    subtitle['file_name']= subtitle['file_name'][0]

with open("subtitles.json", "w") as file:
    json.dump(subtitles, file)