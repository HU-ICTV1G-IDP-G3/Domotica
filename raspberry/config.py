import os

def LoadConfig():
    f = open(os.path.join(os.path.dirname(__file__), 'config'), 'r')
    config = {}

    for line in f.readlines():
        l = line.split(" ")
        config[l[0]] = l[1].replace('\n', '')

    f.close()
    return config
