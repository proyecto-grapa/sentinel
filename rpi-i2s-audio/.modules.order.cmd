cmd_/home/pi/sentinel/rpi-i2s-audio/modules.order := {   echo /home/pi/sentinel/rpi-i2s-audio/my_loader.ko; :; } | awk '!x[$$0]++' - > /home/pi/sentinel/rpi-i2s-audio/modules.order
