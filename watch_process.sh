#!/bin/sh
unset IFS
inotifywait -m -e close_write \
  --timefmt '%Y_%m_%d|%H:%M:%S' \
  --format '%w %f %e %T' \
  /Recordings \
| while read dir filename event datetime; do
  ffmpeg -y -loglevel 0 -f s24le -ar 48k -ac 2 -i $dir$filename -f s16le - |  /home/pi/sentinel/soundscape_process.py  
  mv -n $dir$filename "$dir$(date -d "$(stat -c '%x' $dir$filename)" +"%Y_%m_%d_%H_%M_%S").pcm" 
  /home/pi/sentinel/gsm_send.py
done

