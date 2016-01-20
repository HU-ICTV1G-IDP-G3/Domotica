#/usr/bin/env python2

import raspberry

import time

def Main():
    raspberry.SetupRaspberry()

    while True:
        if raspberry.UpdateHelpButton():
            print "Help Button Pressed"

if __name__ == "__main__":
    Main()
