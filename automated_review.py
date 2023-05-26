#!/usr/bin/python3

# Reading the config file
import json

# Custom key combinations
from pynput import keyboard

import os
# Configuration Loading
with open('config.json', 'r') as config_file:
    CONFIG = json.load(config_file)["automated_review"]

class CompletionException(Exception):
    pass

def on_press(key):
    print(key)
    # if key.char in list(CONFIG["hotkeys"].values()):
    #     if key.char == CONFIG["hotkeys"]["continue"]:
    #         pass
    #     elif key.char == CONFIG["hotkeys"]["back"]:
    #         pass
    #     elif key.char == CONFIG["hotkeys"]["finish"]:
    #         raise CompletionException("Execution has been terminated")
        
            
def main():
    open(CONFIG["output_file"], "w").close()
    with open(CONFIG["output_file"], 'r') as file:
        while(1):
            try:
                with keyboard.Listener(on_press=on_press) as listener:
                    listener.join()
            except CompletionException as e:
                print(e)
                break


# Execution
if __name__ == "__main__":
    main()
