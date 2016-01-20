#/usr/bin/env python2

import raspberry
import database
import config

import time

conf = {}

def Main():
    global conf
    conf = config.LoadConfig()

    raspberry.SetupRaspberry()
    database.SetDatabaseCredentials(conf['host'], conf['user'], conf['password'], conf['database'])

    database.ConnectDatabase()
    UpdateLights()
    database.DisconnectDatabase()

    while True:
        database.ConnectDatabase()

        if raspberry.UpdateHelpButton():
            print "Help Button Pressed"
        UpdateLights()

        database.DisconnectDatabase()

        time.sleep(0.1)


def UpdateLights():
    global conf

    lightstatus = database.GetLightStatus()
    for light in lightstatus:
        lightOn = False
        if light['turnedon'] != 0:
            lightOn = True
        if light['idLight'] == int(conf['light1']):
            raspberry.SetLight1(lightOn)
        if light['idLight'] == int(conf['light2']):
            raspberry.SetLight2(lightOn)
        if light['idLight'] == int(conf['light3']):
            raspberry.SetLight3(lightOn)

if __name__ == "__main__":
    try:
        Main()
    except KeyboardInterrupt:
        print "Disconnecting from database"
        try:
            database.DisconnectDatabase()
        except Exception:
            pass
