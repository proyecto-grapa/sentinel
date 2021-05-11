# EN CONSTRUCCION, esto no anda todavia
# Preparacion

preparar:
	sudo apt update
	sudo apt upgrade

# sudo raspi-config

dependencias:
	sudo apt install raspberrypi-kernel-headers ladspa-sdk inotify-tools libatlas-base-dev
	python3 -m pip install --upgrade pip
	#sudo python3 -m pip install --upgrade pip
	sudo python3 -m pip install scipy pyyaml
	
# WARNING: The scripts f2py, f2py3 and f2py3.7 are installed in '/home/pi/.local/bin' which is not on PATH.
# export PATH := /home/pi/.local/bin:$(PATH)


###    # Activar i2s editando  /boot/config.txt:
###    # Uncomment some or all of these to enable the optional hardware interfaces
###    dtparam=i2s=on
#sudo sed 's/#dtparam=i2s=on/dtparam=i2s=on/' /boot/config.txt 

i2s:
	sudo cp /boot/config.txt /boot/config-bk.txt
	sudo cp configs/boot/config.txt /boot/config.txt

asound:
	sudo cp configs/etc/asound.conf /etc/asound.conf

###	esto es para makefile no correr en linea de comandos
VERSION = $(shell uname -r)
PWD = $(shell pwd)'/rpi-i2s-audio'
i2s-audio:
	cd rpi-i2s-audio
	make -C /lib/modules/$(VERSION)/build M=$(PWD) modules

###	En linea de comandos desde sentinel/
###	cd rpi-i2s-audio
###	make -C /lib/modules/$(uname -r)/build M=$(pwd)/rpi-i2s-audio modules
###     sudo insmod my_loader.ko
###    	sudo cp my_loader.ko /lib/modules/$(uname -r)/kernel/drivers/
###    
###    # Agregar my_loader en una nueva linea en /etc/modules
###    # /etc/modules: kernel modules to load at boot time.
###    # This file contains the names of kernel modules that should be loaded
###    # at boot time, one per line. Lines beginning with "#" are ignored.
###    i2c-dev
###    my_loader
###    
###    sudo depmod
###    sudo reboot
###    # DESPUES DE REBOOT

pinstate:
	wget https://github.com/joan2937/pigpio/archive/master.zip
	unzip master.zip
	cd pigpio-master
	make
	sudo make install
	gcc -Wall -pthread -o pinstate pinstate.c -lpigpio -lrt
	sudo cp pinstate /usr/bin/

###    
###    
###    
###    # Copiar los scripts que están en la subcarpeta scripts a /home/pi y otorgar
###    # permisos de ejecución a los .py y .sh (si hiciera falta)
###    
###    #NO estan mas en scripts cp -r scripts/ /home/pi/
###    chmod +x /home/pi/sentinel/
###    


###    # Testeo
###    # Probar si anda recordings con 
###    ./recording.sh

servicios:
	# Crear la carpeta /Recordings
	sudo mkdir /Recordings
	sudo cp services/*.service /etc/systemd/system/
	sudo systemctl enable watch_process.service
	sudo systemctl enable pinstate.service

###    # Deberia empezar a grabar tramos de 60 segundos
###    # de PCM en Recordings
###    # (cortarlo con crtl+C o killall arecord)  

###    # Probar el watch_process
###    # Y luego arrancar recording en background
###    ./watch_process.sh


###    # # Acoustic field
###    # git clone https://www.github.com/meguia/acoustic_field
###    # # Y después para actualizar
###    # cd acoustic_field
###    # git fetch --all
###    # git pull origin

