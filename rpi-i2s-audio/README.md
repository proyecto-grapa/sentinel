# rpi-i2s-audio
```
sudo apt-get install raspberrypi-kernel-headers
make -C /lib/modules/$(uname -r )/build M=$(pwd) modules
sudo insmod my_loader.ko
```
