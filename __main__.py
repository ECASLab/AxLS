
from os import path
import sys


CONFIG_FILE = "poisonoak/poisonoak.config"
HELP_FILE = "poisonoak/poisonoak.help"


def trim(text):
    '''
    Remove the spaces between text

    Parameters
    ----------
    text : string
        text with white spaces

    Returns
    -------
    string
        text without white spaces
    '''
    return text.replace(" ", "").replace("\n","")


def read_config():
    '''
    Read the config file to check everything is there

    Returns
    -------
    boolean
        True if all the variables are defined and correct
    '''
    if (path.exists(CONFIG_FILE)):
        with open(CONFIG_FILE) as config:
            for line in config.readlines():
                if len(line) > 10:
                    var, value = trim(line).split("=")
                    if var == "RTL" and path.exists(value):
                        print (value, "CHECK")
                    else:
                        print(f"Option {var} is incorrect")
                        return False
        return True
    else:
        print("Config File does not exists!")


for arg in sys.argv:
    if (arg == "-h" or arg == "--help"):
        with open(HELP_FILE) as help:
            print(help.read())
    else:
        read_config()
