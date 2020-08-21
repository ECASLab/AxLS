
from datetime import datetime
import random
import string

def get_name(length):
    timestamp = datetime.now().strftime("%H%M%S")
    unique = ""
    for x in range(length):
        unique += random.choice(string.ascii_letters)
    return f"{timestamp}{unique}"
