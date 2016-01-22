#/usr/bin/env python2

import os
import subprocess
import signal

import database
import config

import time

import socket
import struct
import fcntl

STREAM_PID = 0
DEVNULL = None

def Main():
    global conf
    global DEVNULL

    DEVNULL = open("/dev/null", 'w')

    conf = config.LoadConfig()

    database.SetDatabaseCredentials(conf['host'], conf['user'], conf['password'], conf['database'])

    currentCamera = None

    ip = GetIP()
    print ip

    while True:
        database.ConnectDatabase()
        cameraStatus = database.GetCameraStatus(conf['woning'])

        if cameraStatus['camera'] != currentCamera:
            print "Camera Changed"
            currentCamera = cameraStatus['camera']
            if cameraStatus['camera'] == 1:
                database.SetCameraURL(conf['camera1'], "http://%s:8080/?action=stream" % (ip,))
                StartStream()
                print "Waiting for new request"
            else:
                database.SetCameraURL(conf['camera1'], "nocamera.png")
                StopStream()
                print "Waiting for new request"

        database.DisconnectDatabase()

        time.sleep(0.5)

def StartStream():
    global STREAM_PID
    global DEVNULL

    if STREAM_PID == 0:
        print "Starting Stream"

        p = subprocess.Popen(["/home/pi/bin/mjpg_streamer", "-i", "/home/pi/bin/input_uvc.so -d /dev/video0 -n -y -f 15 -r 640x480", "-o", "/home/pi/bin/output_http.so -n"], stdout=DEVNULL, shell=False)
        STREAM_PID = p.pid
        time.sleep(5)

def StopStream():
    global STREAM_PID

    if STREAM_PID != 0:
        print "Stopping Stream"

        os.kill(STREAM_PID, signal.SIGINT)
        STREAM_PID = 0
        time.sleep(5)

def GetIP():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockfd = sock.fileno()
    SIOCGIFADDR = 0x8915

    ifreq = struct.pack('16sH14s', 'eth0', socket.AF_INET, '\x00' * 14)
    try:
        res = fcntl.ioctl(sockfd, SIOCGIFADDR, ifreq)
    except Exception:
        return None
    ip = struct.unpack('16sH2x4s8x', res)[2]
    return socket.inet_ntoa(ip)

if __name__ == "__main__":
    try:
        Main()
    except KeyboardInterrupt:
        DEVNULL.close()
        try:
            database.DisconnectDatabase()
        except Exception:
            pass
