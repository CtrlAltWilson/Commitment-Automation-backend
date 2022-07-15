import json

def togglecheck():
    global autorun
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