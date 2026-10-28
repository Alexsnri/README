#!/bin/bash
set -e
D=/tmp/claude-0/-home-user-README/4be6a5f7-ac07-5cd5-8b8b-7a17b68ea14a/scratchpad/anim
OUT=/home/user/README/quincy/marketing/video/animados
cd $D
python3 reels_def.py "$@" > /dev/null
for id in "$@"; do
  s=$(date +%s)
  node render.js $D/build $id --out $D/build/$id-video.mp4
  python3 audio.py $id > /dev/null
  ffmpeg -loglevel error -y -i $D/build/$id-mix.wav -af "loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 $D/build/$id-norm.wav
  ffmpeg -loglevel error -y -i $D/build/$id-video.mp4 -i $D/build/$id-norm.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart $OUT/reel-$id.mp4
  echo "$id done in $(( $(date +%s) - s ))s"
done
