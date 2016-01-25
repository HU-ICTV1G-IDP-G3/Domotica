import RPi.GPIO as GPIO

# Define the pins on which the lights and help button is connected
HELP_BUTTON_PIN = 7

LIGHT1_PIN = 11
LIGHT2_PIN = 13
LIGHT3_PIN = 15

HELP_BUTTON_STATUS = False

# Initialize the raspberry so the GPIO pins can be used
def SetupRaspberry():
    global HELP_BUTTON_STATUS

    # Set in which mode the pins are adressed and disable warnings
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    # Setup which pins are used as input
    GPIO.setup(HELP_BUTTON_PIN, GPIO.IN)

    # Setup which pins are used as output
    GPIO.setup(LIGHT1_PIN, GPIO.OUT)
    GPIO.setup(LIGHT2_PIN, GPIO.OUT)
    GPIO.setup(LIGHT3_PIN, GPIO.OUT)

    # Initialize default values
    HELP_BUTTON_STATUS = False
    SetLight1(False)
    SetLight2(False)
    SetLight3(False)

# Check if help button is pressed
def GetHelpButton():
    tmp = GPIO.input(HELP_BUTTON_PIN)
    if tmp == 0:
        return False # Return false if not
    else:
        return True # Return true if pressed

# Check if the help button pressed changed from last time
def UpdateHelpButton():
    global HELP_BUTTON_STATUS

    if GetHelpButton(): # Check if pressed
        if HELP_BUTTON_STATUS == False: # If pressed but not pressed before return true
            HELP_BUTTON_STATUS = True
            return True
    else:
        HELP_BUTTON_STATUS = False

    # Otherwise return false
    return False

# Set light1 on or off
def SetLight1(parValue):
    GPIO.output(LIGHT1_PIN, parValue)

# Set light2 on or off
def SetLight2(parValue):
    GPIO.output(LIGHT2_PIN, parValue)

# Set light3 on or off
def SetLight3(parValue):
    GPIO.output(LIGHT3_PIN, parValue)
