import os

# Load the config file into a dictionary
def LoadConfig():
    #Open the config file and create an empty dictionary
    f = open(os.path.join(os.path.dirname(__file__), 'config'), 'r')
    config = {}

    # Loop through all the lines in the file and store the first word as key and second as value split by a space
    for line in f.readlines():
        l = line.split(" ")
        config[l[0]] = l[1].replace('\n', '')

    # Close the file and return the dictionary
    f.close()
    return config
