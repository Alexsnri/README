#!/bin/bash
set -e
# Uso: scripts/reels/pipeline.sh <id>…  (deja reel-<id>.mp4 en marketing/video/animados)
D="$(cd "$(dirname "$0")" && pwd)"
OUT="${OUT:-$D/../../marketing/video/animados}"
mkdir -p "$D/build" "$OUT"
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
