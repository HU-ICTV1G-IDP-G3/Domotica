import pymysql.cursors

CONNECTION = None
HOST = "127.0.0.1"
USER = 'domotica'
PASSWORD = 'domotica'
DATABASE = 'domotica_db'

def SetDatabaseCredentials(host, user, password, database):
    global HOST
    global USER
    global PASSWORD
    global DATABASE

    HOST = host
    USER = user
    PASSWORD = password
    DATABASE = database

def ConnectDatabase():
    global CONNECTION
    global HOST
    global USER
    global PASSWORD
    global DATABASE

    CONNECTION = pymysql.connect(host = HOST, user = USER, password = PASSWORD, db = DATABASE, charset = 'utf8mb4', cursorclass = pymysql.cursors.DictCursor)

def DisconnectDatabase():
    global CONNECTION

    CONNECTION.close()

def SetHelpButton(woning, value):
    try:
        with CONNECTION.cursor() as cursor:
            sql = "UPDATE `Woning` SET `helpbutton`=%s WHERE `idUser`=%s;"
            cursor.execute(sql, (str(value), woning))

        CONNECTION.commit()
    except Exception as e:
        print e

def GetLightStatus():
    try:
        with CONNECTION.cursor() as cursor:
            sql = "SELECT * FROM Light;"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
    except Exception as e:
        print e

def GetCameraStatus(woning):
    try:
        with CONNECTION.cursor() as cursor:
            sql = "SELECT * FROM `Woning` WHERE `idWoning`=%s;"
            cursor.execute(sql, (woning,))
            result = cursor.fetchone()
            return result
    except Exception as e:
        print e
