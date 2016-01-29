#/usr/bin/env python2

import raspberry
import database
import config

import time

conf = {}

# Main code
def Main():
    # Load config into a global variable conf
    global conf
    conf = config.LoadConfig()

    # Setup the raspberry GPIO pins and set the database login info
    raspberry.SetupRaspberry()
    database.SetDatabaseCredentials(conf['host'], conf['user'], conf['password'], conf['database'])

    # Update the lights with the database
    database.ConnectDatabase()
    UpdateLights()
    database.DisconnectDatabase()

    # Infinite loop to keep checking the database for updates
    while True:
        database.ConnectDatabase()

        # Update the help button if it got pressed and update the lights
        if raspberry.UpdateHelpButton():
            database.SetHelpButton(conf['woning'], 1);
        UpdateLights()

        database.UpdateWoningTimestamp(conf['woning'])

        database.DisconnectDatabase()

        # Delay before the next update happens
        time.sleep(0.1)

# Update the lights
def UpdateLights():
    global conf

    # Get the status which lights need to be on and off
    lightstatus = database.GetLightStatus()
    for light in lightstatus:
        # Set the variable lightOn to true or false depending if the light needs to be on or off
        lightOn = False
        if light['turnedon'] != 0:
            lightOn = True
        if light['idLight'] == int(conf['light1']):
            raspberry.SetLight1(lightOn) # If the id is that of light1 update light1
        if light['idLight'] == int(conf['light2']):
            raspberry.SetLight2(lightOn) # If the id is that of light2 update light2
        if light['idLight'] == int(conf['light3']):
            raspberry.SetLight3(lightOn) # If the id is that of light3 update light3

# If this script is run and not imported
if __name__ == "__main__":
    try:
        Main() # Run main function
    except KeyboardInterrupt:
        # If a KeyboardInterrupt is given, try disconnecting from the database before closing
        print "Disconnecting from database"
        try:
            database.DisconnectDatabase()
        except Exception:
            pass
