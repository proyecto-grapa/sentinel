#!/bin/sh
DIR=$1
for filename in $DIR*.pcm; do
  echo "procesing $filename"
  ffmpeg -y -loglevel 0 -f s24le -ar 48k -ac 2 -i $filename -f s16le - |  /home/pi/sentinel/soundscape_process.py --date $filename 
done

