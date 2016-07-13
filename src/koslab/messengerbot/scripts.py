import morepath
from koslab.messengerbot.hub import App
import yaml
import sys
import os

def start_hub():
    if len(sys.argv) == 1:
        print "%s [config.yml]"
        print "Config file is required"
        sys.exit(1)

    sys.path.append(os.getcwd())
    config = yaml.load(open(sys.argv[1]).read())
    @App.setting_section(section='config')
    def config_section():
        return config

    morepath.run(App(config))
