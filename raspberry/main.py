#/usr/bin/env python2

import raspberry
import database
import config

import time

def Main():
    conf = config.LoadConfig()

    raspberry.SetupRaspberry()
    database.SetDatabaseCredentials(conf['host'], conf['user'], conf['password'], conf['database'])

    database.ConnectDatabase()
    database.GetLightStatus()
    database.DisconnectDatabase()

    while True:
        if raspberry.UpdateHelpButton():
            print "Help Button Pressed"

if __name__ == "__main__":
    Main()
