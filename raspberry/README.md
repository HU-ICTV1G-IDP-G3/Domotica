# Domotica Raspberry Pi

## Dependencies
* RPi
* PyMySQL

## Config
|Key     |      Description|
|:-------|----------------:|
|host    |      database ip|
|user    |    database user|
|password|database password|
|database|    database name|
|light1  |     id of light1|
|light2  |     id of light2|
|light3  |     id of light3|
|woning  |     id of woning|
|camera1 |    id of camera1|

## Installation
```Bash
# Go to home directory
cd

# Create the bin directory
mkdir bin
cd bin

# Clone the repository
git clone https://github.com/HU-ICTV1G-IDP-G3/Domotica.git
cd Domotica/raspberry

# Update the config file (See config for more information)
nano config
cd ../..

# Install MJPG streamer dependencies
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install subversion libjpeg8-dev imagemagick

# Download MJPG streamer
svn co https://svn.code.sf.net/p/mjpg-streamer/code/mjpg-streamer/ mjpg-streamer
cd mjpg-streamer

# Build MJPG streamer
make
cp *.so ../
cp mjpg_streamer ../
cd ../

# Make everything start on boot
sudo crontab -e
# Add in the following lines
@reboot screen -S stream -d -m /usr/bin/python2 /home/pi/bin/Domotica/raspberry/streaming.py
@reboot screen -S lights -d -m /usr/bin/python2 /home/pi/bin/Domotica/raspberry/main.py
# Save the crontab

# Enabling the crontab
sudo systemctl enable cron
sudo systemctl start cron

# Reboot and the system should work fine
sudo reboot
```
