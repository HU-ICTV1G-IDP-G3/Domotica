import pymysql.cursors

import time

CONNECTION = None
HOST = "127.0.0.1"
USER = 'domotica'
PASSWORD = 'domotica'
DATABASE = 'domotica_db'

# Set database log in information so the code can connect to the database on demand
def SetDatabaseCredentials(host, user, password, database):
    # Define which variables are global
    global HOST
    global USER
    global PASSWORD
    global DATABASE

    # Set the variables
    HOST = host
    USER = user
    PASSWORD = password
    DATABASE = database

# Connect to the database so sql queries can be executed
def ConnectDatabase():
    # Define which variables are global
    global CONNECTION
    global HOST
    global USER
    global PASSWORD
    global DATABASE

    # Retry connecting until a succesfull connection is established
    connected = False
    while not connected:
        try:
            CONNECTION = pymysql.connect(host = HOST, user = USER, password = PASSWORD, db = DATABASE, charset = 'utf8mb4', cursorclass = pymysql.cursors.DictCursor) # Connect to the database
            connected = True # Escape while loop if connection is successfull, otherwise the exception was raised in the previous function
        except Exception:
            time.sleep(5) # Sleep for 5 seconds to delay the attempts

# Disconnect from the database
def DisconnectDatabase():
    # Define which variables are global
    global CONNECTION

    CONNECTION.close() # Close the connection to the database

# Update the value of the help button in the database
def SetHelpButton(woning, value):
    try:
        with CONNECTION.cursor() as cursor:
            sql = "UPDATE `Woning` SET `helpbutton`=%s WHERE `idWoning`=%s;"
            cursor.execute(sql, (str(value), woning))

        CONNECTION.commit() # Make sure the changes are updated in the database
    except Exception as e:
        print e

# Get the status of the lights
def GetLightStatus():
    try:
        with CONNECTION.cursor() as cursor:
            sql = "SELECT * FROM Light;"
            cursor.execute(sql)
            result = cursor.fetchall() # Get all the results
            return result # And return them back
    except Exception as e:
        print e

# Get the status of the camera
def GetCameraStatus(woning):
    try:
        with CONNECTION.cursor() as cursor:
            sql = "SELECT * FROM `Woning` WHERE `idWoning`=%s;"
            cursor.execute(sql, (woning,))
            result = cursor.fetchone() # Fetch the first result (as there should only be one result)
            return result # And return it
    except Exception as e:
        print e

# Update the URL of the camera
def SetCameraURL(camera, url):
    try:
        with CONNECTION.cursor() as cursor:
            sql = "UPDATE `Camera` SET `url`=%s WHERE `idCamera`=%s;"
            cursor.execute(sql, (url, str(camera)))

        CONNECTION.commit() # Make sure the changes are updated in the database
    except Exception as e:
        print e

# Update the timestamp to confirm that the raspberry is still up
def UpdateWoningTimestamp(woning):
    try:
        with CONNECTION.cursor() as cursor:
            sql = "UPDATE `Woning` SET `date`=Timestamp(%s) WHERE `idWoning`=%s;"
            cursor.execute(sql, (time.strftime('%Y-%m-%d %H:%M:%S'), woning))

        CONNECTION.commit() # Make sure the changes are updated in the database
    except Exception as e:
        print e
