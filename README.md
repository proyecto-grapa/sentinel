# Sentinel

## Software

1. Script de control general a través de los pulsadores: pinstate.c, corre sudo
   en el momento del inicio. Qué hace, lee cada 0.1 s el estado de la gpio y si
detecta que el pulsador es detectado por más de una cantidad determinada de
segundos cambia de estado: (0 inicio, 1 grabando y con el módulo GSM prendido,
2 shutdown)

2. Servicio watch_process.sh que arranca en el inicio. Qué hace. Vigila la
   carpeta /home/pi/recordings y si se cierra un archivo (PCM) lo procesa con
soundscape_process.py, luego lo renombra colocando la fecha y la hora en que
fue cerrado, y finalmente invoca gsm_send.py para enviar por GSM lo que está en
la cola.

3. Servicio recording.sh que no arranca en el inicio sino cuando se pasa al
   estado 1. Que hace. Graba con los MEMS en PCM de forma continua y va
cortando pedazos de una cantidad determinada de bytes correspondientes a una
duración fijada, y luego los pasa a 24 bits con ffmpeg y los va guardando en la
carpeta /home/pi/recordings

Pinstate
Usa la libreria pigpio
http://abyz.me.uk/rpi/pigpio/

--------------------------------------------------------------------------------

