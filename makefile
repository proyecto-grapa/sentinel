# EN CONSTRUCCION, esto no anda todavia
# Preparacion
sudo apt update
sudo apt upgrade
sudo raspi-config

# Dependencias
sudo apt install raspberrypi-kernel-headers ladspa-sdk inotify-tools libatlas-base-dev
python3 -m pip install scipy pyyaml

# Activar i2s editando  /boot/config.txt:
# Uncomment some or all of these to enable the optional hardware interfaces
dtparam=i2s=on

cd rpi-i2s-audio
make -C /lib/modules/$(uname -r )/build M=$(pwd) modules
sudo insmod my_loader.ko
sudo cp my_loader.ko /lib/modules/$(uname -r)/kernel/drivers/

# Agregar my_loader en una nueva linea en /etc/modules
# /etc/modules: kernel modules to load at boot time.
# This file contains the names of kernel modules that should be loaded
# at boot time, one per line. Lines beginning with "#" are ignored.
i2c-dev
my_loader

sudo depmod
sudo reboot

# DESPUES DE REBOOT


# Copiar los scripts que están en la subcarpeta scripts a /home/pi y otorgar
# permisos de ejecución a los .py y .sh (si hiciera falta)

cp -r scripts/ /home/pi/
chmod +x /home/pi/scripts/

# Testeo

# Crear la carpeta /home/pi/Recordings

mkdir Recordings

# Probar si anda recordings con 

./recording.sh

# Deberia empezar a grabar tramos de 60 segundos de PCM en Recordings (cortarlo con crtl+C)

# Probar el watch_process

# Arrancar recording en background
# Y luego
./watch_process.sh

# # Acoustic field
# git clone https://www.github.com/meguia/acoustic_field
# # Y después para actualizar
# cd acoustic_field
# git fetch --all
# git pull origin
