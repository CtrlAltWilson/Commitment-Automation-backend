import json

def togglecheck():
    with open('config.json','r') as f:
        config = json.load(f)

    if config['autorun'] == False:
        config['autorun'] = True
    else:
        config['autorun'] = False

    with open('config.json','w') as f:
        json.dump(config, f)

def checkautorun():
    try:
        with open('config.json','r') as f:
            config = json.load(f)
    except:
        config = {}
        config['autorun'] = False
        with open('config.json','w') as f:
            json.dump(config, f)
    return config['autorun']

def getMinutes():
    try:
        with open('config.json','r') as f:
            config = json.load(f)
        return config['minutes']
    except:
        min = setMinutes()
    return min

def setMinutes(minutes = 2):
    try:
        with open('config.json','r') as f:
            config = json.load(f)
        config['minutes'] = minutes
        with open('config.json','w') as f:
            json.dump(config, f)
    except:
        with open('config.json','r') as f:
            config = json.load(f)
        addmin = {'minutes':minutes}
        config.update(addmin)
        with open('config.json','w') as f:
            json.dump(config, f)
    return config['minutes']