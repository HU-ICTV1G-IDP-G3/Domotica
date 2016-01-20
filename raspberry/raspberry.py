import RPi.GPIO as GPIO

HELP_BUTTON_PIN = 7

LIGHT1_PIN = 11
LIGHT2_PIN = 13
LIGHT3_PIN = 15

HELP_BUTTON_STATUS = False

def SetupRaspberry():
    global HELP_BUTTON_STATUS

    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    GPIO.setup(HELP_BUTTON_PIN, GPIO.IN)

    GPIO.setup(LIGHT1_PIN, GPIO.OUT)
    GPIO.setup(LIGHT2_PIN, GPIO.OUT)
    GPIO.setup(LIGHT3_PIN, GPIO.OUT)

    HELP_BUTTON_STATUS = False
    SetLight1(False)
    SetLight2(False)
    SetLight3(False)

def GetHelpButton():
    tmp = GPIO.input(HELP_BUTTON_PIN)
    if tmp == 0:
        return False
    else:
        return True

def UpdateHelpButton():
    global HELP_BUTTON_STATUS

    if GetHelpButton():
        if HELP_BUTTON_STATUS == False:
            HELP_BUTTON_STATUS = True
            return True
    else:
        HELP_BUTTON_STATUS = False
    return False

def SetLight1(parValue):
    GPIO.output(LIGHT1_PIN, parValue)

def SetLight2(parValue):
    GPIO.output(LIGHT2_PIN, parValue)

def SetLight3(parValue):
    GPIO.output(LIGHT3_PIN, parValue)
