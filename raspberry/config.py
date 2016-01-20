def LoadConfig():
    f = open('config', 'r')
    config = {}

    for line in f.readlines():
        l = line.split(" ")
        config[l[0]] = l[1].replace('\n', '')

    f.close()
    return config
