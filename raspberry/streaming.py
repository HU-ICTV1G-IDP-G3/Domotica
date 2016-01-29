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

# Global variables
STREAM_PID = 0
DEVNULL = None

# Main streaming functie
def Main():
    global conf
    global DEVNULL

    # Open a file to discard anything written to it
    DEVNULL = open("/dev/null", 'w')

    # Load config
    conf = config.LoadConfig()

    # Set database login info
    database.SetDatabaseCredentials(conf['host'], conf['user'], conf['password'], conf['database'])

    # Set current camera to None so it has to be updated
    currentCamera = None

    # Get own ip to know streaming url
    ip = conf['ip']

    # Infinite loop to update streaming
    while True:
        # Check if camera enabled
        database.ConnectDatabase()
        cameraStatus = database.GetCameraStatus(conf['woning'])

        # If camerastatus changed
        if cameraStatus['camera'] != currentCamera:
            print "Camera Changed"
            currentCamera = cameraStatus['camera']
            if cameraStatus['camera'] == 1: # If it turned on set stream url and start the stream
                database.SetCameraURL(conf['camera1'], "http://%s:8080/?action=stream" % (ip,))
                StartStream()
                print "Waiting for new request"
            else: # Otherwise set the url to offline camera and stop stream
                database.SetCameraURL(conf['camera1'], "/static/img/offline.png")
                StopStream()
                print "Waiting for new request"

        database.DisconnectDatabase()

        # Delay before next check if the status changed
        time.sleep(0.5)

# Start streaming
def StartStream():
    global STREAM_PID
    global DEVNULL

    # Check if there isn't a stream already running and if not start one
    if STREAM_PID == 0:
        print "Starting Stream"

        # Create a new subprocess to stream the camera
        p = subprocess.Popen(["/home/pi/bin/mjpg_streamer", "-i", "/home/pi/bin/input_uvc.so -d /dev/video0 -n -y -f 15 -r 640x480", "-o", "/home/pi/bin/output_http.so -n"], stdout=DEVNULL, shell=False)
        STREAM_PID = p.pid
        time.sleep(5) # Wait 5 seconds to not accept new changes untill the stream has finished starting

# Stop streaming
def StopStream():
    global STREAM_PID

    # Check if there is a stream running
    if STREAM_PID != 0:
        print "Stopping Stream"

        # Kill the stream with a signal that stops the stream in a natural way
        os.kill(STREAM_PID, signal.SIGINT)
        STREAM_PID = 0
        time.sleep(5) # Give the stream 5 seconds to stop before accepting new changes

# Check if script is run and not imported
if __name__ == "__main__":
    try:
        # Run main function
        Main()
    except KeyboardInterrupt:
        DEVNULL.close() # Close dev zero stream
        try:
            database.DisconnectDatabase() # Try disconnecting from database
        except Exception:
            pass
